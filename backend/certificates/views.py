from django.http import HttpResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Certificate, CertificateTemplate
from .services import get_certificate_data, create_certificate_record, generate_certificate_pdf

class GenerateCertificateView(APIView):
    def post(self, request):
        # We expect manual data in request.data
        data_dict = get_certificate_data(request.data)
        
        try:
            certificate = create_certificate_record(data_dict)
            
            # Now instead of returning a static URL, we return the URL to view it dynamically
            view_url = request.build_absolute_uri(f"/api/certificates/view/{certificate.unique_code}/")
            
            return Response({
                "message": "Certificate record created successfully",
                "certificate_url": view_url,
                "unique_code": str(certificate.unique_code)
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ViewCertificateView(APIView):
    def get(self, request, unique_code):
        # Fetch the certificate record
        certificate = get_object_or_404(Certificate, unique_code=unique_code)
        
        # Get the default template or any template
        template = CertificateTemplate.objects.filter(is_default=True).first()
        if not template:
            template = CertificateTemplate.objects.first()
            
        try:
            # Generate the PDF on the fly
            pdf_bytes = generate_certificate_pdf(certificate, template)
            
            # Return it as an HTTP response
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="cert_{certificate.unique_code}.pdf"'
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
