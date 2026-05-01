from reportlab.lib.pagesizes import A4, LETTER, landscape
from reportlab.pdfgen import canvas
from PIL import Image
import os

def convert_images_to_pdf(image_paths, output_path, options):
    page_size = A4
    if options.get('page_size') == 'letter':
        page_size = LETTER
    if options.get('orientation') == 'landscape':
        page_size = landscape(page_size)

    W, H = page_size
    margin = options.get('margin', 20)
    fit_mode = options.get('fit_mode', 'fit')  # 'fit', 'fill', or 'original'
    add_filename = options.get('add_filename', False)
    bg_color = options.get('bg_color', '#ffffff')

    c = canvas.Canvas(output_path, pagesize=page_size)

    # Parse background color hex to RGB 0-1
    bg_hex = bg_color.lstrip('#')
    bg_r = int(bg_hex[0:2], 16) / 255
    bg_g = int(bg_hex[2:4], 16) / 255
    bg_b = int(bg_hex[4:6], 16) / 255

    for img_path in image_paths:
        img = Image.open(img_path)
        img_w, img_h = img.size

        # Fill page background
        from reportlab.lib import colors
        c.setFillColorRGB(bg_r, bg_g, bg_b)
        c.rect(0, 0, W, H, fill=1, stroke=0)

        usable_w = W - 2 * margin
        usable_h = H - 2 * margin
        label_space = 20 if add_filename else 0

        if fit_mode == 'fill':
            # Scale to fill entire page (may crop)
            scale = max(usable_w / img_w, (usable_h - label_space) / img_h)
        elif fit_mode == 'original':
            scale = 1.0  # No scaling
        else:  # 'fit' — default, no cropping
            scale = min(usable_w / img_w, (usable_h - label_space) / img_h)

        new_w = img_w * scale
        new_h = img_h * scale

        # Center the image
        x = (W - new_w) / 2
        y = (H - new_h) / 2
        if add_filename:
            y = (H - new_h - label_space) / 2 + label_space

        c.drawImage(img_path, x, y, width=new_w, height=new_h,
                    preserveAspectRatio=True, mask='auto')

        # Optional filename label
        if add_filename:
            filename = os.path.basename(img_path)
            c.setFillColorRGB(0.4, 0.4, 0.4)
            c.setFont('Helvetica', 9)
            c.drawCentredString(W / 2, margin / 2, filename)

        c.showPage()  # Next image = next page

    c.save()