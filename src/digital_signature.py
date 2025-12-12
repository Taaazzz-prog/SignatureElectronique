"""
Module de signature électronique avec pyHanko
Permet d'ajouter des signatures numériques certifiées aux PDFs
"""

import os
from datetime import datetime
from pathlib import Path

from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec
from pyhanko.sign.signers.pdf_signer import PdfSigner
from pyhanko.sign import timestamps

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime as dt


class DigitalSigner:
    """Gestionnaire de signatures électroniques"""
    
    def __init__(self, cert_dir='certificates'):
        self.cert_dir = cert_dir
        os.makedirs(cert_dir, exist_ok=True)
        self.cert_path = os.path.join(cert_dir, 'signing_cert.pfx')
        self.cert_password = b'signature_app_2025'  # À changer en production
        
    def generate_self_signed_certificate(self, organization="SignatureApp", 
                                        common_name="Signature Électronique",
                                        email="contact@taaazzz-prog.fr"):
        """
        Génère un certificat auto-signé pour les tests
        ATTENTION: Pour l'INPI, il faut un certificat qualifié d'une autorité agréée
        """
        # Générer une clé privée
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        
        # Créer le certificat
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "FR"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "France"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            dt.datetime.utcnow()
        ).not_valid_after(
            dt.datetime.utcnow() + dt.timedelta(days=3650)  # 10 ans
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=True,  # Non-repudiation
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        ).add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.EMAIL_PROTECTION,
                ExtendedKeyUsageOID.CODE_SIGNING,
            ]),
            critical=False
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # Sauvegarder au format PKCS#12 (.pfx)
        from cryptography.hazmat.primitives.serialization import pkcs12
        
        pfx_data = pkcs12.serialize_key_and_certificates(
            name=common_name.encode('utf-8'),
            key=private_key,
            cert=cert,
            cas=None,
            encryption_algorithm=serialization.BestAvailableEncryption(self.cert_password)
        )
        
        with open(self.cert_path, 'wb') as f:
            f.write(pfx_data)
        
        print(f"✅ Certificat auto-signé créé : {self.cert_path}")
        return self.cert_path
    
    def load_signer(self):
        """Charge le signataire depuis le certificat"""
        if not os.path.exists(self.cert_path):
            print("⚠️  Certificat introuvable, création d'un certificat auto-signé...")
            self.generate_self_signed_certificate()
        
        return signers.SimpleSigner.load_pkcs12(
            pfx_file=self.cert_path,
            passphrase=self.cert_password
        )
    
    def sign_pdf(self, input_path, output_path, reason="Document signé électroniquement",
                 location="France", contact_info=None, visible=True, 
                 page_num=None, position=None):
        """
        Signe électroniquement un PDF
        
        Args:
            input_path: Chemin du PDF à signer
            output_path: Chemin du PDF signé
            reason: Raison de la signature
            location: Lieu de signature
            contact_info: Informations de contact
            visible: Si True, ajoute une signature visible
            page_num: Numéro de page pour la signature visible (None = dernière page)
            position: Position (x, y, width, height) pour la signature visible
        """
        try:
            # Charger le signataire
            signer = self.load_signer()
            
            # Préparer la signature
            if visible and position:
                x, y, width, height = position
                # pyHanko utilise (x1, y1, x2, y2)
                sig_field_spec = SigFieldSpec(
                    sig_field_name='Signature',
                    box=(x, y, x + width, y + height),
                    on_page=page_num
                )
            else:
                sig_field_spec = None
            
            # Ouvrir le PDF en mode incrémental
            with open(input_path, 'rb') as inf:
                w = IncrementalPdfFileWriter(inf)
                
                # Créer les métadonnées de signature
                meta = signers.PdfSignatureMetadata(
                    field_name='Signature',
                    reason=reason,
                    location=location,
                    contact_info=contact_info or "contact@taaazzz-prog.fr"
                )
                
                # Signer le document
                if sig_field_spec:
                    pdf_signer = PdfSigner(
                        meta, 
                        signer=signer,
                        signature_appearance=sig_field_spec
                    )
                else:
                    pdf_signer = PdfSigner(meta, signer=signer)
                
                # Écrire le PDF signé
                with open(output_path, 'wb') as outf:
                    pdf_signer.sign_pdf(w, output=outf)
            
            return True, "PDF signé avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la signature : {str(e)}"
    
    def verify_signature(self, pdf_path):
        """
        Vérifie les signatures d'un PDF
        Retourne la liste des signatures et leur validité
        """
        try:
            from pyhanko.sign.validation import validate_pdf_signature
            from pyhanko.pdf_utils.reader import PdfFileReader
            
            signatures = []
            
            with open(pdf_path, 'rb') as f:
                reader = PdfFileReader(f)
                sig_fields = reader.embedded_signatures
                
                for sig_field in sig_fields:
                    try:
                        status = validate_pdf_signature(sig_field)
                        signatures.append({
                            'field_name': sig_field.field_name,
                            'valid': status.bottom_line,
                            'signer': status.signer_name,
                            'timestamp': status.signing_cert.not_valid_before
                        })
                    except Exception as e:
                        signatures.append({
                            'field_name': sig_field.field_name,
                            'valid': False,
                            'error': str(e)
                        })
            
            return True, signatures
            
        except Exception as e:
            return False, f"Erreur lors de la vérification : {str(e)}"


# Instance globale
_digital_signer = None

def get_digital_signer():
    """Retourne l'instance unique du signataire"""
    global _digital_signer
    if _digital_signer is None:
        _digital_signer = DigitalSigner()
    return _digital_signer
