import fitz
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

class ExtractImagesFromPDF(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
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
                image_path = f"media/pdf_images/{image_filename}"

                # Save the image using Django's storage system
                image_file = ContentFile(image_bytes)
                saved_path = default_storage.save(image_path, image_file)

                # Store the saved image path
                saved_image_paths.append(saved_path)

        # Return the paths of the saved images
        return Response({
            "message": "Images extracted successfully.",
            "saved_images": saved_image_paths
        })
