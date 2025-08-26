"""
SSL/HTTPS configuration for phStudio.
Cost-effective SSL setup with Let's Encrypt integration for production.
Development support with self-signed certificates.
"""

import os
import ssl
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import json

logger = logging.getLogger(__name__)


class SSLManager:
    """
    Cost-effective SSL certificate management.
    Supports Let's Encrypt for production and self-signed for development.
    """
    
    def __init__(self, domain: str = "localhost", email: str = "admin@localhost"):
        self.domain = domain
        self.email = email
        self.cert_dir = Path("/etc/ssl/certs/phstudio")
        self.cert_dir.mkdir(parents=True, exist_ok=True)
        
        # Certificate paths
        self.cert_file = self.cert_dir / "cert.pem"
        self.key_file = self.cert_dir / "key.pem"
        self.chain_file = self.cert_dir / "chain.pem"
        self.fullchain_file = self.cert_dir / "fullchain.pem"
    
    def generate_self_signed_cert(self) -> bool:
        """
        Generate self-signed certificate for development.
        Uses OpenSSL command line tool (free).
        """
        try:
            # Create certificate configuration
            config_content = f"""
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=US
ST=State
L=City
O=phStudio
CN={self.domain}

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = {self.domain}
DNS.2 = www.{self.domain}
DNS.3 = localhost
IP.1 = 127.0.0.1
"""
            
            config_file = self.cert_dir / "cert.conf"
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            # Generate private key and certificate
            cmd = [
                "openssl", "req", "-new", "-x509", "-days", "365",
                "-nodes", "-out", str(self.cert_file),
                "-keyout", str(self.key_file),
                "-config", str(config_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Self-signed certificate generated for {self.domain}")
                return True
            else:
                logger.error(f"Failed to generate self-signed certificate: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error generating self-signed certificate: {str(e)}")
            return False
    
    def setup_letsencrypt(self) -> bool:
        """
        Set up Let's Encrypt certificate for production.
        Uses certbot (free) for automatic certificate management.
        """
        try:
            # Check if certbot is available
            result = subprocess.run(["which", "certbot"], capture_output=True)
            if result.returncode != 0:
                logger.error("Certbot not found. Install with: sudo apt-get install certbot")
                return False
            
            # Request certificate
            cmd = [
                "certbot", "certonly",
                "--standalone",
                "--non-interactive",
                "--agree-tos",
                "--email", self.email,
                "-d", self.domain
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Copy certificates to our directory
                letsencrypt_dir = Path(f"/etc/letsencrypt/live/{self.domain}")
                if letsencrypt_dir.exists():
                    import shutil
                    shutil.copy2(letsencrypt_dir / "cert.pem", self.cert_file)
                    shutil.copy2(letsencrypt_dir / "privkey.pem", self.key_file)
                    shutil.copy2(letsencrypt_dir / "chain.pem", self.chain_file)
                    shutil.copy2(letsencrypt_dir / "fullchain.pem", self.fullchain_file)
                    
                    logger.info(f"Let's Encrypt certificate obtained for {self.domain}")
                    return True
            
            logger.error(f"Failed to obtain Let's Encrypt certificate: {result.stderr}")
            return False
            
        except Exception as e:
            logger.error(f"Error setting up Let's Encrypt: {str(e)}")
            return False
    
    def renew_certificate(self) -> bool:
        """Renew Let's Encrypt certificate"""
        try:
            result = subprocess.run(["certbot", "renew", "--quiet"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Certificate renewed successfully")
                return True
            else:
                logger.error(f"Certificate renewal failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error renewing certificate: {str(e)}")
            return False
    
    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        """
        Create SSL context for HTTPS server.
        Returns None if certificates are not available.
        """
        if not (self.cert_file.exists() and self.key_file.exists()):
            logger.warning("SSL certificates not found")
            return None
        
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(str(self.cert_file), str(self.key_file))
            
            # Security settings
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS")
            context.options |= ssl.OP_NO_SSLv2
            context.options |= ssl.OP_NO_SSLv3
            context.options |= ssl.OP_NO_TLSv1
            context.options |= ssl.OP_NO_TLSv1_1
            context.options |= ssl.OP_SINGLE_DH_USE
            context.options |= ssl.OP_SINGLE_ECDH_USE
            
            return context
            
        except Exception as e:
            logger.error(f"Error creating SSL context: {str(e)}")
            return None
    
    def check_certificate_expiry(self) -> Optional[int]:
        """
        Check certificate expiry in days.
        Returns None if certificate is not available.
        """
        if not self.cert_file.exists():
            return None
        
        try:
            cmd = ["openssl", "x509", "-in", str(self.cert_file), "-noout", "-dates"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('notAfter='):
                        expiry_str = line.split('=', 1)[1]
                        from datetime import datetime
                        expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                        days_remaining = (expiry_date - datetime.now()).days
                        return days_remaining
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking certificate expiry: {str(e)}")
            return None


class SecurityConfigManager:
    """
    Manages security configuration for different environments.
    Cost-effective approach using configuration files.
    """
    
    def __init__(self, env: str = "development"):
        self.env = env
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
    
    def generate_security_config(self) -> Dict[str, Any]:
        """Generate security configuration based on environment"""
        base_config = {
            "security_headers": {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
            },
            "cors": {
                "allow_credentials": True,
                "max_age": 86400
            },
            "rate_limiting": {
                "requests_per_minute": 120,
                "burst_limit": 200
            }
        }
        
        if self.env == "production":
            base_config.update({
                "ssl": {
                    "enabled": True,
                    "redirect_http": True,
                    "hsts_max_age": 31536000,
                    "hsts_include_subdomains": True
                },
                "security_headers": {
                    **base_config["security_headers"],
                    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                    "Content-Security-Policy": self._get_production_csp()
                },
                "cors": {
                    **base_config["cors"],
                    "allow_origins": ["https://yourdomain.com"]
                }
            })
        else:
            base_config.update({
                "ssl": {
                    "enabled": False,
                    "redirect_http": False
                },
                "security_headers": {
                    **base_config["security_headers"],
                    "Content-Security-Policy": self._get_development_csp()
                },
                "cors": {
                    **base_config["cors"],
                    "allow_origins": ["http://localhost:3000", "http://localhost:5173"]
                }
            })
        
        return base_config
    
    def _get_production_csp(self) -> str:
        """Get production Content Security Policy"""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.telegram.org; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    def _get_development_csp(self) -> str:
        """Get development Content Security Policy (more permissive)"""
        return (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: http:; "
            "connect-src 'self' https://api.telegram.org ws: wss: http: https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save security configuration to file"""
        config_file = self.config_dir / f"security_{self.env}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Security configuration saved to {config_file}")
    
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load security configuration from file"""
        config_file = self.config_dir / f"security_{self.env}.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return None


# Production HTTPS startup script
def setup_production_https(domain: str, email: str) -> bool:
    """
    Set up HTTPS for production deployment.
    Cost-effective using Let's Encrypt.
    """
    ssl_manager = SSLManager(domain, email)
    
    # Try to obtain Let's Encrypt certificate
    if ssl_manager.setup_letsencrypt():
        logger.info("HTTPS setup completed with Let's Encrypt")
        return True
    else:
        logger.warning("Let's Encrypt failed, falling back to self-signed certificate")
        return ssl_manager.generate_self_signed_cert()


# Development HTTPS setup
def setup_development_https(domain: str = "localhost") -> bool:
    """Set up HTTPS for development with self-signed certificate"""
    ssl_manager = SSLManager(domain)
    return ssl_manager.generate_self_signed_cert()


# Global instances
ssl_manager = SSLManager()
security_config_manager = SecurityConfigManager()