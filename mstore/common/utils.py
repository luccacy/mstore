import os
import errno
import hashlib
import os
import sys
import uuid

import prettytable

from mstore.common import exc
from mstore.common import importutils


from ConfigParser import ConfigParser, NoSectionError, NoOptionError, \
    RawConfigParser

def split_path(path, minsegs=1, maxsegs=None, rest_with_last=False):
    """
    Validate and split the given HTTP request path.

    **Examples**::

        ['a'] = split_path('/a')
        ['a', None] = split_path('/a', 1, 2)
        ['a', 'c'] = split_path('/a/c', 1, 2)
        ['a', 'c', 'o/r'] = split_path('/a/c/o/r', 1, 3, True)

    :param path: HTTP Request path to be split
    :param minsegs: Minimum number of segments to be extracted
    :param maxsegs: Maximum number of segments to be extracted
    :param rest_with_last: If True, trailing data will be returned as part
                           of last segment.  If False, and there is
                           trailing data, raises ValueError.
    :returns: list of segments with a length of maxsegs (non-existant
              segments will return as None)
    :raises: ValueError if given an invalid path
    """
    if not maxsegs:
        maxsegs = minsegs
    if minsegs > maxsegs:
        raise ValueError('minsegs > maxsegs: %d > %d' % (minsegs, maxsegs))
    if rest_with_last:
        segs = path.split('/', maxsegs)
        minsegs += 1
        maxsegs += 1
        count = len(segs)
        if (segs[0] or count < minsegs or count > maxsegs or
                '' in segs[1:minsegs]):
            raise ValueError('Invalid path: %s' % quote(path))
    else:
        minsegs += 1
        maxsegs += 1
        segs = path.split('/', maxsegs)
        count = len(segs)
        if (segs[0] or count < minsegs or count > maxsegs + 1 or
                '' in segs[1:minsegs] or
                (count == maxsegs + 1 and segs[maxsegs])):
            raise ValueError('Invalid path: %s' % quote(path))
    segs = segs[1:maxsegs]
    segs.extend([None] * (maxsegs - 1 - len(segs)))
    return segs

def reiterate(iterable):
    """
    Consume the first item from an iterator, then re-chain it to the rest of
    the iterator.  This is useful when you want to make sure the prologue to
    downstream generators have been executed before continuing.

    :param iterable: an iterable object
    """
    if isinstance(iterable, (list, tuple)):
        return iterable
    else:
        iterator = iter(iterable)
        try:
            chunk = ''
            while not chunk:
                chunk = next(iterator)
            return itertools.chain([chunk], iterator)
        except StopIteration:
            return []

def config_true_value(value):
    """
    Returns True if the value is either True or a string in TRUE_VALUES.
    Returns False otherwise.
    """
    return value is True or \
        (isinstance(value, basestring) and value.lower() in TRUE_VALUES)

def parse_options(parser=None, once=False, test_args=None):
    """
    Parse standard mstore server/daemon options with optparse.OptionParser.

    :param parser: OptionParser to use. If not sent one will be created.
    :param once: Boolean indicating the "once" option is available
    :param test_args: Override sys.argv; used in testing

    :returns : Tuple of (config, options); config is an absolute path to the
               config file, options is the parser options as a dictionary.

    :raises SystemExit: First arg (CONFIG) is required, file must exist
    """
    if not parser:
        parser = OptionParser(usage="%prog CONFIG [options]")
    parser.add_option("-v", "--verbose", default=False, action="store_true",
                      help="log to console")
    if once:
        parser.add_option("-o", "--once", default=False, action="store_true",
                          help="only run one pass of daemon")

    # if test_args is None, optparse will use sys.argv[:1]
    options, args = parser.parse_args(args=test_args)

    if not args:
        parser.print_usage()
        print _("Error: missing config file argument")
        sys.exit(1)
    config = os.path.abspath(args.pop(0))
    if not os.path.exists(config):
        parser.print_usage()
        print _("Error: unable to locate %s") % config
        sys.exit(1)

    extra_args = []
    # if any named options appear in remaining args, set the option to True
    for arg in args:
        if arg in options.__dict__:
            setattr(options, arg, True)
        else:
            extra_args.append(arg)

    options = vars(options)
    if extra_args:
        options['extra_args'] = extra_args
    return config, options 

# Decorator for cli-args
def arg(*args, **kwargs):
    def _decorator(func):
        # Because of the sematics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator


def pretty_choice_list(l):
    return ', '.join("'%s'" % i for i in l)


def print_list(objs, fields, formatters={}):
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.align = 'l'

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                field_name = field.lower().replace(' ', '_')
                data = getattr(o, field_name, None) or ''
                row.append(data)
        pt.add_row(row)

    print ensure_str(pt.get_string())


def print_dict(d):
    pt = prettytable.PrettyTable(['Property', 'Value'], caching=False)
    pt.align = 'l'
    [pt.add_row(list(r)) for r in d.iteritems()]
    print ensure_str(pt.get_string(sortby='Property'))


def find_resource(manager, name_or_id):
    """Helper for the _find_* methods."""
    # first try to get entity as integer id
    try:
        if isinstance(name_or_id, int) or name_or_id.isdigit():
            return manager.get(int(name_or_id))
    except exc.NotFound:
        pass

    # now try to get entity as uuid
    try:
        uuid.UUID(ensure_str(name_or_id))
        return manager.get(name_or_id)
    except (ValueError, exc.NotFound):
        pass

    # finally try to find entity by name
    matches = list(manager.list(filters={'name': name_or_id}))
    num_matches = len(matches)
    if num_matches == 0:
        msg = "No %s with a name or ID of '%s' exists." % \
              (manager.resource_class.__name__.lower(), name_or_id)
        raise exc.CommandError(msg)
    elif num_matches > 1:
        msg = ("Multiple %s matches found for '%s', use an ID to be more"
               " specific." % (manager.resource_class.__name__.lower(),
                               name_or_id))
        raise exc.CommandError(msg)
    else:
        return matches[0]


def skip_authentication(f):
    """Function decorator used to indicate a caller may be unauthenticated."""
    f.require_authentication = False
    return f


def is_authentication_required(f):
    """Checks to see if the function requires authentication.

    Use the skip_authentication decorator to indicate a caller may
    skip the authentication step.
    """
    return getattr(f, 'require_authentication', True)


def string_to_bool(arg):
    return arg.strip().lower() in ('t', 'true', 'yes', '1')


def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.
    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def import_versioned_module(version, submodule=None):
    module = 'glanceclient.v%s' % version
    if submodule:
        module = '.'.join((module, submodule))
    return importutils.import_module(module)


def exit(msg=''):
    if msg:
        print >> sys.stderr, ensure_str(msg)
    sys.exit(1)


def save_image(data, path):
    """
    Save an image to the specified path.

    :param data: binary data of the image
    :param path: path to save the image to
    """
    if path is None:
        image = sys.stdout
    else:
        image = open(path, 'wb')
    try:
        for chunk in data:
            image.write(chunk)
    finally:
        if path is not None:
            image.close()


def integrity_iter(iter, checksum):
    """
    Check image data integrity.

    :raises: IOError
    """
    md5sum = hashlib.md5()
    for chunk in iter:
        yield chunk
        md5sum.update(chunk)
    md5sum = md5sum.hexdigest()
    if md5sum != checksum:
        raise IOError(errno.EPIPE,
                      'Corrupt image download. Checksum was %s expected %s' %
                      (md5sum, checksum))


def make_size_human_readable(size):
    suffix = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']
    base = 1024.0

    index = 0
    while size >= base:
        index = index + 1
        size = size / base

    padded = '%.1f' % size
    stripped = padded.rstrip('0').rstrip('.')

    return '%s%s' % (stripped, suffix[index])


def ensure_unicode(text, incoming=None, errors='strict'):
    """
    Decodes incoming objects using `incoming` if they're
    not already unicode.

    :param incoming: Text's current encoding
    :param errors: Errors handling policy.
    :returns: text or a unicode `incoming` encoded
                representation of it.
    """
    if isinstance(text, unicode):
        return text

    if not incoming:
        incoming = sys.stdin.encoding or \
            sys.getdefaultencoding()

    # Calling `str` in case text is a non str
    # object.
    text = str(text)
    try:
        return text.decode(incoming, errors)
    except UnicodeDecodeError:
        # Note(flaper87) If we get here, it means that
        # sys.stdin.encoding / sys.getdefaultencoding
        # didn't return a suitable encoding to decode
        # text. This happens mostly when global LANG
        # var is not set correctly and there's no
        # default encoding. In this case, most likely
        # python will use ASCII or ANSI encoders as
        # default encodings but they won't be capable
        # of decoding non-ASCII characters.
        #
        # Also, UTF-8 is being used since it's an ASCII
        # extension.
        return text.decode('utf-8', errors)


def ensure_str(text, incoming=None,
               encoding='utf-8', errors='strict'):
    """
    Encodes incoming objects using `encoding`. If
    incoming is not specified, text is expected to
    be encoded with current python's default encoding.
    (`sys.getdefaultencoding`)

    :param incoming: Text's current encoding
    :param encoding: Expected encoding for text (Default UTF-8)
    :param errors: Errors handling policy.
    :returns: text or a bytestring `encoding` encoded
                representation of it.
    """

    if not incoming:
        incoming = sys.stdin.encoding or \
            sys.getdefaultencoding()

    if not isinstance(text, basestring):
        # try to convert `text` to string
        # This allows this method for receiving
        # objs that can be converted to string
        text = str(text)

    if isinstance(text, unicode):
        return text.encode(encoding, errors)
    elif text and encoding != incoming:
        # Decode text before encoding it with `encoding`
        text = ensure_unicode(text, incoming, errors)
        return text.encode(encoding, errors)

    return text
