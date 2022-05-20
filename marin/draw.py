from PIL import Image, ImageDraw, ImageFont
from requests import get
from io import BytesIO


CARD_SIZE = (1000, 400)
AVATAR_BORDER = 10
FONT_SIZE = 40

font = ImageFont.truetype('./assets/font.ttf', FONT_SIZE)


backgrounds = {
    '1': ('./assets/backgrounds/lines.jpg', (0, 0, 0)),
    '2': ('./assets/backgrounds/vaporwave-1.jpg', (0, 0, 0)),
    '3': ('./assets/backgrounds/vaporwave-2.jpg', (0, 0, 0))
}
layouts = {
    'username': {
        'avatar': lambda size: (CARD_SIZE[0] // 2 - size[0] // 2, CARD_SIZE[1] // 2 - size[1] // 2),
        'username': lambda size: (CARD_SIZE[0] // 2, CARD_SIZE[1] // 2 + size[1] // 2 + AVATAR_BORDER + (CARD_SIZE[1] - (CARD_SIZE[1] // 2 + size[1] // 2 + AVATAR_BORDER)) // 2)
    },
    'text_center': {
        'avatar': lambda size: (CARD_SIZE[0] // 2 - size[0] // 2, CARD_SIZE[1] // 2 - size[1] // 2 - CARD_SIZE[1] // 8),
        'username': lambda size: (CARD_SIZE[0] // 2, layouts['text_center']['avatar'](size)[1] + size[1] + FONT_SIZE // 1.2),
        'text': lambda size: (CARD_SIZE[0] // 2, layouts['text_center']['username'](size)[1] + FONT_SIZE * 1.2)
    },
}


def draw_welcome_card(lo, bg: tuple, accent: str | tuple, user_name, user_avatar, text=None):
    if bg[0] == 'colour':
        im = Image.new('RGB', CARD_SIZE, bg[1])
    else:
        bg = backgrounds[bg[0]]
        im = Image.open(bg[0])

    d = ImageDraw.Draw(im)

    # User avatar
    avatar = Image.open(BytesIO(get(user_avatar).content)
                        ).convert('RGBA').resize((280, 280))
    mask = Image.new('L', avatar.size)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, *avatar.size), fill=255)
    pos = layouts[lo]['avatar'](avatar.size)

    d.ellipse(((pos[0] - AVATAR_BORDER, pos[1] - AVATAR_BORDER), (pos[0] + AVATAR_BORDER +
              avatar.size[0], pos[1] + AVATAR_BORDER + avatar.size[0])), accent)
    im.paste(avatar, pos, mask)

    # Username
    pos = layouts[lo]['username'](avatar.size)
    d.text(pos, user_name, (0, 0, 0) if (
        bg[1][0]*0.299 + bg[1][1]*0.587 + bg[1][2]*0.114) > 186 else (255, 255, 255), font, 'mm')

    # Additional text
    if 'text' in layouts[lo]:
        pos = layouts[lo]['text'](avatar.size)
        d.text(pos, text, (0, 0, 0) if (
            bg[1][0]*0.299 + bg[1][1]*0.587 + bg[1][2]*0.114) > 186 else (255, 255, 255), font, 'mm')

    return im
