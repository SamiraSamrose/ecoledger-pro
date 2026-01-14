import os
import uuid
import hashlib
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path
from datetime import datetime
import logging
from backend.database.models import db, Document
from config.settings import Config

logger = logging.getLogger(__name__)

class DocumentProcessor:
    
    def __init__(self):
        self.upload_folder = Config.UPLOAD_FOLDER
        self.confidence_threshold = Config.OCR_CONFIDENCE_THRESHOLD
        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        try:
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            
            denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
            
            coords = np.column_stack(np.where(denoised > 0))
            if len(coords) > 0:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                
                (h, w) = denoised.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(
                    denoised, M, (w, h),
                    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
                )
                
                return Image.fromarray(rotated)
            else:
                return Image.fromarray(denoised)
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return image
    
    def extract_text_with_confidence(self, image):
        """Extract text from image with confidence score"""
        try:
            ocr_data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT
            )
            
            confidences = [int(conf) for conf in ocr_data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            text = pytesseract.image_to_string(image)
            
            return {
                'text': text,
                'confidence': avg_confidence / 100,
                'word_count': len(text.split()),
                'line_count': len(text.split('\n'))
            }
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return {
                'text': '',
                'confidence': 0,
                'word_count': 0,
                'line_count': 0
            }
    
    def classify_document(self, text):
        """Classify document type based on content"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['deed', 'property', 'real estate', 'title']):
            return 'Property Deed'
        elif any(keyword in text_lower for keyword in ['energy certificate', 'efficiency rating', 'kwh', 'energy performance']):
            return 'Energy Certificate'
        elif any(keyword in text_lower for keyword in ['passport', 'identification', 'driver license', 'national id']):
            return 'Identity Document'
        elif any(keyword in text_lower for keyword in ['financial statement', 'balance sheet', 'income statement', 'audit']):
            return 'Financial Statement'
        elif any(keyword in text_lower for keyword in ['business license', 'incorporation', 'registration']):
            return 'Business License'
        else:
            return 'Other Document'
    
    def extract_structured_data(self, text, doc_type):
        """Extract structured data from text based on document type"""
        import re
        
        data = {}
        
        try:
            if doc_type == 'Property Deed':
                address_pattern = r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)'
                addresses = re.findall(address_pattern, text)
                if addresses:
                    data['property_address'] = addresses[0]
                
                value_pattern = r'\$[\d,]+(?:\.\d{2})?'
                values = re.findall(value_pattern, text)
                if values:
                    data['property_value'] = values[0]
            
            elif doc_type == 'Energy Certificate':
                cert_pattern = r'[A-Z]{2}\d{6,}'
                certs = re.findall(cert_pattern, text)
                if certs:
                    data['certificate_number'] = certs[0]
                
                rating_pattern = r'Rating[:\s]+([A-E])'
                ratings = re.findall(rating_pattern, text, re.IGNORECASE)
                if ratings:
                    data['energy_rating'] = ratings[0]
                
                kwh_pattern = r'(\d+)\s*kWh'
                kwh_values = re.findall(kwh_pattern, text, re.IGNORECASE)
                if kwh_values:
                    data['annual_kwh_savings'] = int(kwh_values[0])
            
            elif doc_type == 'Identity Document':
                id_pattern = r'(?:ID|No|Number)[:\s]+(\w+)'
                ids = re.findall(id_pattern, text, re.IGNORECASE)
                if ids:
                    data['id_number'] = ids[0]
                
                name_pattern = r'Name[:\s]+([A-Za-z\s]+)'
                names = re.findall(name_pattern, text, re.IGNORECASE)
                if names:
                    data['name'] = names[0].strip()
            
            elif doc_type == 'Financial Statement':
                revenue_pattern = r'(?:Revenue|Income)[:\s]+\$?([\d,]+)'
                revenues = re.findall(revenue_pattern, text, re.IGNORECASE)
                if revenues:
                    data['revenue'] = revenues[0]
                
                assets_pattern = r'(?:Assets|Total Assets)[:\s]+\$?([\d,]+)'
                assets = re.findall(assets_pattern, text, re.IGNORECASE)
                if assets:
                    data['total_assets'] = assets[0]
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {str(e)}")
        
        return data
    
    def process_document(self, file_path, loan_id, doc_type=None):
        """Process uploaded document with OCR"""
        try:
            document_id = f"DOC{str(uuid.uuid4())[:8].upper()}"
            
            file_ext = file_path.lower().split('.')[-1]
            
            if file_ext == 'pdf':
                images = convert_from_path(file_path, dpi=300)
            else:
                images = [Image.open(file_path)]
            
            pages_data = []
            all_text = ''
            
            for idx, image in enumerate(images):
                processed_image = self.preprocess_image(image)
                page_result = self.extract_text_with_confidence(processed_image)
                page_result['page_number'] = idx + 1
                pages_data.append(page_result)
                all_text += page_result['text'] + '\n'
            
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            detected_doc_type = self.classify_document(all_text) if not doc_type else doc_type
            structured_data = self.extract_structured_data(all_text, detected_doc_type)
            
            avg_confidence = sum([p['confidence'] for p in pages_data]) / len(pages_data)
            verification_status = 'Verified' if avg_confidence > self.confidence_threshold else 'Review Required'
            
            file_size = os.path.getsize(file_path)
            
            document = Document(
                document_id=document_id,
                loan_id=loan_id,
                document_type=detected_doc_type,
                upload_timestamp=datetime.utcnow(),
                ocr_confidence=avg_confidence,
                document_hash=file_hash,
                verification_status=verification_status,
                extracted_data={
                    'pages': pages_data,
                    'structured_data': structured_data,
                    'all_text': all_text[:1000]
                },
                file_path=file_path,
                file_size_kb=file_size // 1024,
                page_count=len(pages_data)
            )
            
            db.session.add(document)
            db.session.commit()
            
            logger.info(f"Document {document_id} processed - Type: {detected_doc_type}, Confidence: {avg_confidence:.2f}")
            
            return {
                'document_id': document_id,
                'document_type': detected_doc_type,
                'verification_status': verification_status,
                'ocr_confidence': avg_confidence,
                'page_count': len(pages_data),
                'structured_data': structured_data
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    def get_document(self, document_id):
        """Retrieve document information"""
        try:
            document = Document.query.filter_by(document_id=document_id).first()
            if not document:
                return None
            
            return {
                'document_id': document.document_id,
                'loan_id': document.loan_id,
                'document_type': document.document_type,
                'verification_status': document.verification_status,
                'ocr_confidence': document.ocr_confidence,
                'page_count': document.page_count,
                'file_size_kb': document.file_size_kb,
                'upload_timestamp': document.upload_timestamp.isoformat(),
                'extracted_data': document.extracted_data
            }
            
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return None
    
    def list_documents(self, loan_id=None):
        """List documents for a loan"""
        try:
            query = Document.query
            
            if loan_id:
                query = query.filter(Document.loan_id == loan_id)
            
            documents = query.order_by(Document.upload_timestamp.desc()).all()
            
            return [
                {
                    'document_id': doc.document_id,
                    'loan_id': doc.loan_id,
                    'document_type': doc.document_type,
                    'verification_status': doc.verification_status,
                    'ocr_confidence': doc.ocr_confidence,
                    'upload_timestamp': doc.upload_timestamp.isoformat()
                }
                for doc in documents
            ]
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []
