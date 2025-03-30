# Flet Chat App - Aplicação Avançada

## Funcionalidades Extra Implementadas

### 1. Reação de Mensagens
**Motivação**
A implementação de reações as mensagens, veio da necessidade de transformar as interações em mais dinamicas e expressivas, permitindo que os utilizadores respondam de forma ligeira às mensagens sem precisr escrever respostas completas. Essa ideia, veio da inspiração de aplicações já existentes como, instagram, whatsapp, discord, etc.

**Descrição Tecnica**
- Implementado atraves de um dicionario que guarda emojis como chaves e listas de utilizadores como valores
- Interface dom PopupMenuBUtton para seleção de emojis
- Visualização em tempo real, junto com contadores de reações
- Permanencia das reações no chat, atraves do armazenamento no ficheiro json


**Como Utilizar**
1. Clique em "..." do lado de uma mensagem
2. Selecione uma reação na lista de emojis
3. Para remover, é so clicar na mesma reação


### 2. Busca Avançada de Mensagens
**Motivação**
Em chats ativos, procurar uma mensagem especifica em meio a tanta conversa pode se tornar um empecilho. Essa funcionaliade foi desenvolvida para resolver esse tipo de problema em questão, atraves da procura de uma mensagem, pelo termo utilizado, ou pelo utilizador vinculado.

**Descrição Tecnica**
- Algoritmo de busca case-insensitive
- Destaque visual dos termos encontrados (fundo amarelo)
- Filtragem em tempo real
- Interface com opção de limpeza da pesquisa ou não

**Como Utilizar**
1. Clique no icone de lupa na barra superior
2. Digite o termo de busca no campo aparecido
3. Clique em "Pesquisar"
4. Para "limpar" é só clicar no botão especifico

### 3. Modo Tema escuro/claro
**Motivação**
Acessibilidade e conforto visual foram as principais motivações para essa funiconalidade. Vendo que os utilizadores tem preferencias diferentes e podem usar a aplicação em diversos ambientes luminosos.

**Descrição Tecnica**
- Alternacia dinamica sem recarregamento
- Paleta de cores adaptativa para ambos os temas
- Estado fixo durante a sessão
- Incone dinamico que reflete o tema atual 

**Como Utilizar**
1. Localize o incone de sol/lua no canto superior direito 
2. Clieque para alternar entre os temas
3. O sistema lembrará sua preferencia durante a sessão

## 🛠️ Instalação e Configuração

# Clone o repositório
git clone https://github.com/sophisoares/flet-chat-app.git

# Instale as dependências
pip install flet

# Execute a aplicação
flet run main.py




