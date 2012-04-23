# coding=utf-8
import re
from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.formats import number_format

register = template.Library()


def has_value(field):
    #print field.name, field.field.__class__.__name__
    if field.field.__class__.__name__ == 'RangeField' or field.field.__class__.__name__ == 'NumericRangeField':
        if (field.data[0] == '' and field.data[1] == '') or (field.data[0] is None and field.data[1] is None):
            return 'has_not_value'
    elif field.field.__class__.__name__ == 'Field':
        if field.data is None:
            return 'has_not_value'
    elif field.field.__class__.__name__ == 'NullBooleanField':
        if field.data is None:
            return 'has_not_value'
    elif field.field.__class__.__name__ == 'ChoiceField':
        if field.data is None or field.data == '':
            return 'has_not_value'
    elif field.field.__class__.__name__ == 'MultipleChoiceField':
        # TODO: review below but dont need for this case, 
        # I have got just one always displayed multichoicefield
        if field.data is None:
            return False
    return 'has_value'

register.simple_tag(has_value)

import os
from PIL import Image
from django import template
from django.conf import settings

ERROR_IMG = "settings.DEFAULT_ERROR_IMAGE"

def create_thumbnail_image_file(file, width, height):
    """ Create a thumbnail image and return the path """
    if not file:
        return ERROR_IMG
    
    basename, format = file.name.rsplit('.', 1)
    thumb = basename + '_' + str(width) + 'x' + str(height) + '.' + format
    thumb_filename = os.path.join(settings.MEDIA_ROOT, thumb)
    thumb_url = os.path.join(settings.MEDIA_URL, thumb)
    filename = os.path.join(settings.MEDIA_ROOT, file.name)
    image = Image.open(filename)
    src_width, src_height = image.size
    src_ratio = float(src_width) / float(src_height)
    dst_width, dst_height = width, height
    dst_ratio = float(dst_width) / float(dst_height)
   	
    if dst_ratio < src_ratio:
	    crop_height = src_height
	    crop_width = crop_height * dst_ratio
	    x_offset = float(src_width - crop_width) / 2
	    y_offset = 0
    else:
	    crop_width = src_width
	    crop_height = crop_width / dst_ratio
	    x_offset = 0
	    y_offset = float(src_height - crop_height) / 3
		
    if os.path.exists(thumb_filename):
        if os.path.getmtime(thumb_filename) < os.path.getmtime(filename):
            os.unlink(thumb_filename)
        else:
            return thumb_url


    image = image.crop((int(x_offset), int(y_offset), int(x_offset)+int(crop_width), int(y_offset)+int(crop_height)))
    image = image.resize((int(dst_width), int(dst_height)), Image.ANTIALIAS)

    #image.thumbnail([width, height], Image.ANTIALIAS)
    image.save(thumb_filename, image.format)
    return thumb_url

class ThumbnailerNode(template.Node):
    def __init__(self, image, width, height):
        self.image = image
        self.width = width
        self.height = height
    
    def render(self, context):
        try:
            actual_image = template.resolve_variable(self.image, context)
            return create_thumbnail_image_file(actual_image, self.width, self.height)
        except template.VariableDoesNotExist:
            return ERROR_IMG
          
@register.tag(name="thumbnail")
def thumbnail(parser, token):
    try:
        tag_name, image, width, height = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, " %r tag requires exactly 3 arguments" % token.contents[0]
    return ThumbnailerNode(image, int(width), int(height))

def priceformat(value, use_l10n=True):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    #if settings.USE_L10N and use_l10n:
    '''
        try:
            if not isinstance(value, float):
                value = int(value)
        except (TypeError, ValueError):
            return priceformat(value, False)
        else:
            return number_format(value)
    '''
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1> \g<2>', orig)
    if orig == new:
        return new
    else:
        return priceformat(new, use_l10n)
priceformat.is_safe = True
register.filter(priceformat)