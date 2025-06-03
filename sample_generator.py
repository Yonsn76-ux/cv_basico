# -*- coding: utf-8 -*-
"""
Generador de CVs de ejemplo para diferentes profesiones
"""

import os
import random

def create_sample_cvs(base_directory="sample_cvs"):
    """Crea CVs de ejemplo organizados por profesiones"""
    
    # Crear directorio base
    os.makedirs(base_directory, exist_ok=True)
    
    # Definir profesiones y sus CVs de ejemplo
    professions_data = {
        "Agrónomo": [
            {
                "name": "cv_agronomo_1.txt",
                "content": """
Juan Carlos Pérez García
Ingeniero Agrónomo
Email: juan.perez@email.com
Teléfono: +34 123 456 789

EXPERIENCIA PROFESIONAL:
- Ingeniero Agrónomo Senior en AgroTech Solutions (2020-2024) - 4 años de experiencia
- Especialista en Cultivos en Cooperativa Agrícola del Valle (2018-2020) - 2 años
- Técnico Agrícola Junior en Finca Los Olivos (2017-2018) - 1 año

EDUCACIÓN:
- Ingeniería Agronómica - Universidad Politécnica Agraria (2017)
- Maestría en Agricultura Sostenible - Universidad Nacional (2019)

HABILIDADES TÉCNICAS:
- Manejo de cultivos de cereales, hortalizas y frutales
- Sistemas de riego por goteo y aspersión
- Control integrado de plagas y enfermedades
- Fertilización y nutrición vegetal
- Maquinaria agrícola: tractores, cosechadoras, sembradoras
- Software agrícola: AgroSoft, CropManager
- Análisis de suelos y agua
- Agricultura de precisión con GPS

PROYECTOS:
- Implementación de sistema de riego tecnificado en 500 hectáreas
- Programa de mejoramiento genético de maíz
- Certificación orgánica para cultivos de exportación

CERTIFICACIONES:
- Certificado en Agricultura Orgánica
- Manejo Integrado de Plagas (MIP)
- Operador de Maquinaria Agrícola
"""
            },
            {
                "name": "cv_agronomo_2.txt", 
                "content": """
María Elena Rodríguez López
Ingeniera Agrónoma
Email: maria.rodriguez@agro.com
Teléfono: +34 987 654 321

EXPERIENCIA PROFESIONAL:
- Coordinadora de Producción Agrícola en Hacienda San Miguel (2019-2024) - 5 años
- Asesora Técnica en Fertilizantes del Norte (2017-2019) - 2 años
- Investigadora en Centro de Investigación Agrícola (2016-2017) - 1 año

EDUCACIÓN:
- Ingeniería Agronómica - Universidad Agraria Nacional (2016)
- Especialización en Horticultura - Instituto Tecnológico (2018)

HABILIDADES:
- Producción de hortalizas bajo invernadero
- Manejo de cultivos hidropónicos
- Control biológico de plagas
- Postcosecha y almacenamiento
- Ganadería bovina y porcina
- Administración de fincas
- Comercialización de productos agrícolas
- Extensión rural y capacitación

EXPERIENCIA EN CULTIVOS:
- Tomate, pimiento, pepino bajo invernadero
- Cultivos de campo: maíz, sorgo, frijol
- Frutales: mango, aguacate, cítricos
- Pastos y forrajes para ganadería

LOGROS:
- Incremento del 40% en productividad de tomate
- Reducción del 30% en uso de pesticidas
- Implementación de buenas prácticas agrícolas
"""
            },
            {
                "name": "cv_agronomo_3.txt",
                "content": """
Carlos Alberto Mendoza Silva
Agrónomo Especialista
Email: carlos.mendoza@campo.com
Teléfono: +34 555 123 456

EXPERIENCIA PROFESIONAL:
- Gerente de Producción en Agroindustrias del Pacífico (2021-2024) - 3 años
- Ingeniero de Campo en Cultivos Tropicales SA (2018-2021) - 3 años
- Asistente Técnico en Cooperativa Cafetera (2017-2018) - 1 año

EDUCACIÓN:
- Ingeniería Agronómica - Universidad del Campo (2017)
- Diplomado en Agricultura Orgánica (2019)

ESPECIALIDADES:
- Cultivos tropicales: café, cacao, plátano
- Sistemas agroforestales
- Agricultura sostenible y orgánica
- Manejo de recursos hídricos
- Mecanización agrícola
- Cadenas productivas agrícolas
- Gestión de calidad en agricultura

CONOCIMIENTOS:
- Variedades mejoradas de cultivos
- Técnicas de propagación vegetal
- Manejo integrado de nutrientes
- Agricultura climáticamente inteligente
- Certificaciones internacionales (GlobalGAP, Rainforest)
- Trazabilidad de productos agrícolas

IDIOMAS:
- Español (nativo)
- Inglés (intermedio)
"""
            }
        ],
        
        "Ingeniero de Software": [
            {
                "name": "cv_software_1.txt",
                "content": """
Ana Patricia González Martín
Ingeniera de Software Senior
Email: ana.gonzalez@tech.com
Teléfono: +34 666 777 888

EXPERIENCIA PROFESIONAL:
- Senior Software Engineer en TechCorp (2020-2024) - 4 años de experiencia
- Full Stack Developer en StartupTech (2018-2020) - 2 años
- Junior Developer en SoftwareSolutions (2017-2018) - 1 año

EDUCACIÓN:
- Ingeniería en Sistemas Computacionales - Universidad Tecnológica (2017)
- Maestría en Ciencias de la Computación - Instituto Politécnico (2019)

HABILIDADES TÉCNICAS:
- Lenguajes: Python, Java, JavaScript, TypeScript, C#, Go
- Frontend: React, Angular, Vue.js, HTML5, CSS3, Bootstrap
- Backend: Node.js, Express, Django, Flask, Spring Boot, .NET
- Bases de datos: PostgreSQL, MySQL, MongoDB, Redis
- Cloud: AWS, Azure, Google Cloud Platform
- DevOps: Docker, Kubernetes, Jenkins, GitLab CI/CD
- Herramientas: Git, GitHub, Jira, Confluence

PROYECTOS:
- Desarrollo de plataforma e-commerce con microservicios
- API REST para aplicación móvil con 100k+ usuarios
- Sistema de gestión empresarial con React y Node.js
- Migración de aplicaciones legacy a la nube

CERTIFICACIONES:
- AWS Certified Solutions Architect
- Certified Kubernetes Administrator (CKA)
- Scrum Master Certified
"""
            },
            {
                "name": "cv_software_2.txt",
                "content": """
Roberto Carlos Fernández Ruiz
Desarrollador Full Stack
Email: roberto.fernandez@dev.com
Teléfono: +34 444 555 666

EXPERIENCIA PROFESIONAL:
- Lead Developer en InnovaTech (2019-2024) - 5 años de experiencia
- Software Developer en WebSolutions (2017-2019) - 2 años
- Programador Junior en CodeFactory (2016-2017) - 1 año

EDUCACIÓN:
- Licenciatura en Informática - Universidad de Ciencias (2016)
- Bootcamp Full Stack Development - CodeAcademy (2017)

STACK TECNOLÓGICO:
- Frontend: React, Redux, Next.js, Tailwind CSS
- Backend: Node.js, Express, Python, Django
- Bases de datos: PostgreSQL, MongoDB, Firebase
- Mobile: React Native, Flutter
- Testing: Jest, Cypress, Selenium
- Deployment: Vercel, Netlify, Heroku, DigitalOcean

EXPERIENCIA:
- Desarrollo de aplicaciones web responsivas
- Arquitectura de microservicios
- Integración de APIs de terceros
- Optimización de rendimiento web
- Metodologías ágiles (Scrum, Kanban)
- Code review y mentoring de junior developers

PROYECTOS DESTACADOS:
- Plataforma de streaming con 50k usuarios concurrentes
- Dashboard de analytics en tiempo real
- App móvil de delivery con geolocalización
"""
            }
        ],
        
        "Especialista en Marketing": [
            {
                "name": "cv_marketing_1.txt",
                "content": """
Laura Beatriz Morales Castro
Especialista en Marketing Digital
Email: laura.morales@marketing.com
Teléfono: +34 777 888 999

EXPERIENCIA PROFESIONAL:
- Marketing Manager en DigitalAgency (2021-2024) - 3 años de experiencia
- Especialista en Marketing Digital en BrandCorp (2019-2021) - 2 años
- Coordinadora de Marketing en StartupMedia (2018-2019) - 1 año

EDUCACIÓN:
- Licenciatura en Marketing - Universidad de Negocios (2018)
- Maestría en Marketing Digital - Escuela de Negocios (2020)

HABILIDADES:
- Google Ads, Facebook Ads, LinkedIn Ads, TikTok Ads
- SEO/SEM y optimización de motores de búsqueda
- Email Marketing y Marketing Automation
- Social Media Management y Community Management
- Content Marketing y Copywriting
- Google Analytics, Google Tag Manager
- CRM: HubSpot, Salesforce, Mailchimp
- Diseño: Canva, Adobe Photoshop, Figma

CAMPAÑAS EXITOSAS:
- Campaña de lanzamiento que generó 500% ROI
- Estrategia SEO que incrementó tráfico orgánico 300%
- Campaña en redes sociales con 2M de impresiones
- Email marketing con 25% de tasa de apertura

CERTIFICACIONES:
- Google Ads Certified
- Facebook Blueprint Certification
- HubSpot Content Marketing Certification
- Google Analytics Individual Qualification
"""
            },
            {
                "name": "cv_marketing_2.txt",
                "content": """
Diego Alejandro Vargas Peña
Marketing Manager
Email: diego.vargas@brand.com
Teléfono: +34 333 444 555

EXPERIENCIA PROFESIONAL:
- Head of Marketing en GrowthCompany (2020-2024) - 4 años de experiencia
- Marketing Specialist en RetailBrand (2018-2020) - 2 años
- Asistente de Marketing en AgencyPlus (2017-2018) - 1 año

EDUCACIÓN:
- Licenciatura en Comunicación Social - Universidad Nacional (2017)
- MBA en Marketing - Business School (2019)

ESPECIALIDADES:
- Marketing estratégico y planificación
- Investigación de mercados y análisis de consumidor
- Branding y posicionamiento de marca
- Marketing de influencers y partnerships
- E-commerce y marketplace management
- Performance marketing y growth hacking
- Event marketing y activaciones BTL
- PR y relaciones públicas

LOGROS:
- Incremento de ventas del 150% en 2 años
- Lanzamiento exitoso de 5 productos nuevos
- Reducción del CAC en 40% optimizando campañas
- Construcción de comunidad de 100k seguidores

HERRAMIENTAS:
- Plataformas de ads: Google, Facebook, Instagram, LinkedIn
- Analytics: Google Analytics, Mixpanel, Hotjar
- CRM: Salesforce, HubSpot, Pipedrive
- Email: Mailchimp, SendGrid, Klaviyo
"""
            }
        ],
        
        "Contador": [
            {
                "name": "cv_contador_1.txt",
                "content": """
Patricia Isabel Jiménez Herrera
Contadora Pública Certificada
Email: patricia.jimenez@contabilidad.com
Teléfono: +34 222 333 444

EXPERIENCIA PROFESIONAL:
- Contadora Senior en Corporación Financiera (2019-2024) - 5 años de experiencia
- Analista Contable en Empresa Manufacturera (2017-2019) - 2 años
- Auxiliar Contable en Despacho Contable (2016-2017) - 1 año

EDUCACIÓN:
- Licenciatura en Contaduría Pública - Universidad de Ciencias Económicas (2016)
- Especialización en Auditoría - Instituto de Contadores (2018)

HABILIDADES:
- Contabilidad general y financiera
- Elaboración de estados financieros
- Análisis financiero y presupuestario
- Auditoría interna y externa
- Costos y contabilidad gerencial
- Impuestos y obligaciones fiscales
- NIIF (Normas Internacionales de Información Financiera)
- Software contable: SAP, QuickBooks, ContaPlus, Excel avanzado

RESPONSABILIDADES:
- Cierre contable mensual y anual
- Conciliaciones bancarias y cuentas por cobrar
- Nómina y prestaciones sociales
- Declaraciones de impuestos (IVA, Renta, Industria y Comercio)
- Control de inventarios y activos fijos
- Análisis de variaciones presupuestales

CERTIFICACIONES:
- Contador Público Autorizado
- Certificación en NIIF
- Revisor Fiscal
"""
            }
        ],
        
        "Médico": [
            {
                "name": "cv_medico_1.txt",
                "content": """
Dr. Fernando Andrés López Mendoza
Médico General
Email: fernando.lopez@hospital.com
Teléfono: +34 111 222 333

EXPERIENCIA PROFESIONAL:
- Médico General en Hospital Central (2020-2024) - 4 años de experiencia
- Médico Rural en Centro de Salud San José (2018-2020) - 2 años
- Interno de Medicina en Hospital Universitario (2017-2018) - 1 año

EDUCACIÓN:
- Medicina y Cirugía - Universidad de Medicina (2017)
- Especialización en Medicina Familiar - Hospital Universitario (2019)

HABILIDADES CLÍNICAS:
- Consulta médica general y diagnóstico
- Medicina preventiva y promoción de la salud
- Atención de urgencias médicas
- Procedimientos menores (suturas, curaciones)
- Interpretación de exámenes de laboratorio
- Electrocardiografía básica
- Medicina familiar y comunitaria
- Atención materno-infantil

EXPERIENCIA:
- Atención de pacientes ambulatorios y hospitalizados
- Programas de vacunación y control de crecimiento
- Manejo de enfermedades crónicas (diabetes, hipertensión)
- Educación en salud y prevención de enfermedades
- Trabajo en equipo multidisciplinario
- Historia clínica electrónica

CERTIFICACIONES:
- Registro Médico Nacional
- BLS (Basic Life Support)
- ACLS (Advanced Cardiovascular Life Support)
- Certificación en Medicina Familiar
"""
            }
        ]
    }
    
    created_files = []
    
    # Crear carpetas y archivos para cada profesión
    for profession, cvs in professions_data.items():
        profession_dir = os.path.join(base_directory, profession)
        os.makedirs(profession_dir, exist_ok=True)
        
        for cv_data in cvs:
            file_path = os.path.join(profession_dir, cv_data["name"])
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cv_data["content"].strip())
                created_files.append(file_path)
                print(f"✅ Creado: {file_path}")
            except Exception as e:
                print(f"❌ Error creando {file_path}: {e}")
    
    print(f"\n🎉 ¡CVs de ejemplo creados exitosamente!")
    print(f"📁 Directorio base: {base_directory}")
    print(f"📄 Total de archivos: {len(created_files)}")
    print(f"👥 Profesiones: {len(professions_data)}")
    
    return created_files, base_directory

if __name__ == "__main__":
    create_sample_cvs()
