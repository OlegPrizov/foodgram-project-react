import io

from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.response import Response


def pdf_making(objects):
    pdfmetrics.registerFont(TTFont('FreeSans', './utils/FreeSans.ttf'))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont('FreeSans', 14)
    c.setTitle('СПИСОК ПОКУПОК')
    data = []
    for object in objects:
        data.append(str(
            (f'{object["ingredient_name"]}, '
             f'{object["measurement_unit"]}, '
             f'{object["amount"]}')
        ))
    for line in data:
        textob.textLine(line)
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='recipes.pdf')


def data_aggregartion(serializer, pk, request):
    data = {
        'user': request.user.id,
        'recipe': pk
    }
    pre_serializer = serializer(data=data, context={'request': request})
    pre_serializer.is_valid(raise_exception=True)
    pre_serializer.save()
    return Response(pre_serializer.data, status=status.HTTP_201_CREATED)
