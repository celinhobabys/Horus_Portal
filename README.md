Relatório Microcontroladores ENG 4033

**CONCEITO**

O projeto do nosso grupo se resume a um teclado espião, onde a ideia principal é fazer um adaptador de entrada de teclado PS2 para USB usando um microcontrolador. O ponto chave do trabalho é que o mesmo terá acesso a internet, fazendo com que outra pessoa consiga receber e enviar as teclas do teclado para outra máquina remotamente.

**COMPONENTES**

Para utilização do dispositivo, basta conectar o teclado na porta PS/2 e o USB no computador, ligando automaticamente o microcontrolador e a internet, possibilitando o acesso remoto a ele. Agora temos acesso ao portal desenvolvido para o atacante, o HORUS.

Neste Portal, o atacante pode ver em tempo real as teclas digitadas pelo usuário, assim como “sequestrar” o controle do teclado, bloqueando o acesso da vítima e dando acesso ao atacante em tempo real.

O portal conta com diversas abas, cada uma com um propósito único dentro do escopo do projeto, sendo elas:

HOME
	
Aba principal, onde se tem o recebimento das teclas em tempo real da vítima, o envio de teclas do atacante é o modo “sequestro” mencionado acima.
ROTINAS

Aba onde se montam scripts que serão executados sob demanda, ou em um certo período de tempo, onde o conteúdo desse script será o envio de teclas pré-determinadas pelo atacante.

LOGS

Aba onde se tem um log de todas as teclas pressionadas durante 24 horas, com esses logs podendo ser processados por uma AI integrada no Portal (Gemini), com botão de download para o mesmo.

CONFIGURAÇÕES

Apenas para as preferências do usuário.

**TECNOLOGIAS**

ARDUINO LEONARDO
Um microcontrolador que pode ser lido como um teclado USB para o computador.

**ESQUEMÁTICA CIRCUITO**
Foi utilizado o software Fritizing. Foi utilizado um divisor de tensão para diminuir a tensão (5V) do TX do arduino para o RX do ESP32 (3.3V).
![image](https://github.com/user-attachments/assets/4921ecea-22f8-4678-ab55-c594c4ce0585)

**ARQUITETURA**
Foi utilizado o site draw.io para fazer o diagrama que representa a comunicação entre os componentes arduino, ESP e portal.

