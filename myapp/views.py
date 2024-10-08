from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Summary 
from .serializers import *
from django.conf import settings
from rest_framework import status
import google.generativeai as genai
from PyPDF2 import PdfReader
import fitz
from PIL import Image
from rest_framework.parsers import MultiPartParser, FormParser
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os

model = genai.GenerativeModel('gemini-1.5-flash')
                
class ExtractData(APIView):
    serializer_class = PdfSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        # Get the uploaded PDF file from the request
        pdf_file = request.FILES['file']

        # Use an in-memory BytesIO object to avoid saving the PDF file
        pdf_data = pdf_file.read()
        pdf_stream = BytesIO(pdf_data)

        # Open the PDF file using PyMuPDF
        pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")

        # List to store the saved image paths
        saved_image_paths = []

        # Loop through the pages to extract images
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            image_list = page.get_images(full=True)

            # Loop through each image in the page
            for img_index, img in enumerate(image_list):
                xref = img[0]  # Image XREF
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]  # Get image extension (like jpg, png)

                # Create an in-memory image file
                image = Image.open(BytesIO(image_bytes))

                # Prepare file name and path
                image_filename = f"pdf_image_{page_num+1}_{img_index+1}.{image_ext}"
                image_path = os.path.join('pdf_images', image_filename)

                # Save the image using Django's storage system
                image_file = ContentFile(image_bytes)
                saved_path = default_storage.save(image_path, image_file)
                media_path = settings.MEDIA_URL + saved_path
                # Store the saved image path
                saved_image_paths.append(media_path)
        
        reader = PdfReader(request.FILES.get('file'))  
        data = ""
        for i in range(len(reader.pages)):
            data = data + reader.pages[i].extract_text()
        return Response({"data": data, "saved_images": saved_image_paths},status=status.HTTP_200_OK)

class SummaryView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if file:
            file_content = file.read().decode('utf-8')
            prompt = "Please provide Title and summary for the following content without \n" + file_content
            response = model.generate_content(prompt)
            
            a = response.text
            str_ing = " ".join(a.split())
            # import pdb ; pdb.set_trace()
            
            data = str_ing.split("## Summary: ")
            t = data[0]
            s = data[1]
            temp = t.split("## Title: ")
            title = " ".join(temp[1].split())
            summary = " ".join(s.split())
            
            Summary.objects.create(title=title, summary=summary)
            serializer = SummarySerializer(Summary.objects.all(), many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response({"Error":"Some Error"}, status=status.HTTP_400_BAD_REQUEST)  
    
class SummaryList(APIView):
    def get(self, request):
        summaries = Summary.objects.all()
        if summaries:
            serializer = SummarySerializer(summaries, many=True)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"Error":"Some Error"}, status=status.HTTP_400_BAD_REQUEST)