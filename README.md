🛡️ Sentinel de Rede

Um painel simples em Python para monitorar dispositivos da rede local, mostrando IP, host e latência em tempo real através de uma interface web.

📌 Sobre o projeto

O sistema:

Escaneia a rede local

Mede a latência (ping) de cada dispositivo

Exibe tudo em uma página HTML

Atualiza automaticamente a cada 5 segundos

Mostra um gráfico de latência usando Chart.js

É um projeto escolar feito para demonstrar monitoramento básico de rede.

📂 Estrutura
Sentinel_de_rede/
│
├── app.py
├── devices.py
├── requirements.txt
│
├── templates/
│   └── index.html
│
└── static/
    └── style.css

🚀 Como rodar
1. Clonar o repositório
git clone https://github.com/Lz-acc/Sentinel_de_rede.git
cd Sentinel_de_rede

2. Criar e ativar ambiente

Windows:

python -m venv .venv
.venv\Scripts\activate

3. Instalar dependências
pip install -r requirements.txt

4. Executar
python app.py


Acessar no navegador:

http://localhost:5000

✔ Tecnologias usadas

Python

Flask

HTML + CSS

Chart.js
