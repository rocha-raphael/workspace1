from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
#importar google autenticador
from django.contrib.auth.models import User, Group
from my_project.settings import YOUR_GOOGLE_CLIENT_ID
#importar decor para ver se esta logado
from django.contrib.auth.decorators import login_required
#Autenticar
from django.contrib.auth import logout, authenticate
from django.views.generic import TemplateView
from django.contrib.auth import login as djandoLogin
import re
from django.contrib.auth.mixins import LoginRequiredMixin



# Create your views here.
class index(TemplateView):
    #Nome do template na pasta /templates/
    #Paginas de autenticação, home, login e pagina de recuperação de senha
    pages = {"home":"home.html", "login":"login.html", "r_senha":"rec_senha.html"}

    def get(self, request, *args, **kwargs):
        """
        Método GET para a visualização da página, determinando a página atual com base no status de login do usuário.

        Args:
            request: Objeto de requisição HTTP.

            *args: Argumentos adicionais.
            **kwargs: Argumentos adicionais com palavras-chave.
            user_dict: Dicionario para preencher variaveis das paginas
            current_page: Qual pagina será carregada

        Returns:
            HttpResponse: Renderiza a página inicial, a página de login, dependendo do status de login.
        """
        user_dict = {}
        if request.user.is_authenticated:
            try:
                # Se o usuário estiver logado, define o grupo do usuário e a página inicial.
                user_dict["grupo"] = request.user.groups.first().name
                current_page = self.pages["home"]

            except AttributeError:
                # Tratar caso o usuário não tenha grupos ou request.user seja None.
                current_page = self.pages["login"]
                user_dict["erro_msg"] = (
                    "Ocorreu um problema ao determinar seu grupo de usuário. "
                    "Por favor, entre em contato com o suporte técnico."
                )
        else:
            # Se o usuário não estiver logado, define a página de login.
            current_page = self.pages["login"]
            user_dict['YOUR_GOOGLE_CLIENT_ID'] = YOUR_GOOGLE_CLIENT_ID
        return render(request, current_page, user_dict)

    def post(self, request, *args, **kwargs):

        current_page = self.pages["login"]
        #busca todos os process  do post
        current_dict = self.process_post(request)

        print(current_dict,"AQUIIIIIII")
        current_dict["container"] = request.POST.get('container')
        if current_dict['usuario'] and current_dict['senha']:
            current_page, current_dict['erro_msg'] = self.authenticate_user(current_dict['usuario'], current_dict['senha'])
            print(current_page, current_dict['erro_msg'])

        #Verificar se está autenticado
        if request.user.is_authenticated:

            if request.POST.get('container'):
                if request.POST.get('container') == 'usuarios':
                    return redirect("/index/usuarios/")

                current_dict["container"] = request.POST.get('container')
                current_page = self.pages["home"]

            #Clicando no botao logou deslogar
            if request.POST.get('logout'):
                logout(request)

            #Clicando no recuperar senha direciona para pagina de alteração de senha
            if request.POST.get('c_senha'):
                current_page = self.pages["r_senha"]
            # Ao clicar no botão para alterar a senha, este bloco de código verifica se todos os argumentos
            # necessários estão presentes e valida se as senhas atendem aos padrões estabelecidos.
            # Em caso de sucesso e sem erros, redireciona para a página home.
            if request.POST.get('new_pass'): 
                # Obtenção dos dados necessários do formulário
                usuario = request.POST.get('usuario')
                nova_senha = request.POST.get('nova_senha')
                confirma_nova_senha = request.POST.get('confirma_nova_senha')
                # Validar formato da senha e obter mensagem de erro, se houver
                mensagem_erro = self.validar_formato_senha(request, nova_senha, confirma_nova_senha, usuario)
                if mensagem_erro is None:
                    try:
                        # Alterar a senha do usuário e realizar o login
                        request.user.set_password(str(current_dict['n_senha']))
                        request.user.save()
                        autenticacao = authenticate(username=usuario, password=senha)
                        djandoLogin(request, autenticacao)
                        # Redirecionar para a página home em caso de sucesso
                        current_page = self.pages["home"]
                    except Exception as e:
                        # Tratar erros durante a alteração da senha  e redireciona para pagina de senha
                        current_dict['erro_msg'] = f"Erro {e}."
                        current_page = self.pages["r_senha"]
                else:
                    # Caso haja mensagem de erro na validação da senha e redireciona para pagina de senha
                    current_dict['erro_msg'] = mensagem_erro
                    current_page = self.pages["r_senha"]


        return render(request, current_page, current_dict)

    def process_post(self, request):
        context = {}
        print(request.POST.dict(), "AQUI2")
        if request.method == 'POST':
            print("POSTE")
            context['usuario'] = request.POST.get('usuario')
            context['senha'] = request.POST.get('senha')
            context['container'] = request.POST.get('container')
            print(context['senha'], "ESTA É A SENHA123")
            context['usuario_logado'] = request.user
            context['senha'] = request.POST.get('nova_senha')
            context['n_senha'] = request.POST.get('confirma_nova_senha')
            context["todos_grupos"] = ['supervisor','usuario','admin']
            context["grupo"] = self.verificar_grupo(self.request.user)

            # Add other variables as needed

        return context
    def authenticate_user(self, usuario, senha):
        """
        Função para autenticar um usuário.
    
        Args:
            request: Objeto de requisição HTTP.
            usuario: Nome de usuário fornecido pelo usuário.
            senha: Senha fornecida pelo usuário.
    
        Returns:
            page: pagina a ser direcionada.
            erro_msg: se houver erro 
        """
        autenticacao = authenticate(username=usuario, password=senha)
        if autenticacao:
            djandoLogin(self.request, autenticacao)
            page = self.pages["home"]
            erro_msg = ""
        else:
            # Tratar caso o usuário não tenha grupos ou request.user seja None.
            page = self.pages["login"]
            erro_msg = (
                "Ocorreu um problema ao tentar logar. "
                "Por favor, entre em contato com o suporte técnico."
            )
        return page, erro_msg


    def validar_formato_senha(self, request, senha, n_senha, usuario):
            """
            Verifica a compatibilidade e critérios de formato da senha.
            Retorna uma mensagem de erro se houver algum problema, caso contrário, retorna None.
            """
            # Verificar se as senhas são iguais
            if senha != n_senha:
                return "As senhas não são iguais. Verifique e tente novamente."

            # Verificar se a senha atende aos critérios de formato
            if len(n_senha) < 8:
                return "A senha muito curta, ao menos 8."

            # Verificar se a senha atende aos critérios de formato
            if not re.search(r'[A-Z]', n_senha):
                return "A senha precisa de ao menos 1 caracter maiúsculo."

            # Verificar se o usuário é compatível
            if str(usuario) != str(request.user):
                return "Usuário não compatível"

            # A senha atende aos critérios e é compatível
            return None

    def verificar_grupo(self, user):
        if user.groups.exists():
            # Se sim, obtém o nome do primeiro grupo
            grupo = user.groups.first().name
        else:
            # Se não pertencer a nenhum grupo, define uma mensagem apropriada
            grupo = "Sem grupo"
        return  grupo

class usuarios(LoginRequiredMixin, TemplateView):
    '''
    Essa é a classe do Login, serve para logar recupear senha e autenticar via google

    '''
    #Nome do template na pasta /templates/
    pages = {"home":"home.html", "login":"login.html", "r_senha":"rec_senha.html"}
    current_page = pages['home']
    login_url = '/index/' 

    #current_dict["grupos"] = [grupo.name for grupo in self.request.user.groups.all()]
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["container"] = 'usuarios'
        context["todos_grupos"] = ['usuario','supervisor','admin']
        print(self.request.user)
        context["nomes"]= [nome.username for nome  in User.objects.all() if nome.username not in ['root', str(self.request.user)]]
        context['nome_usuario'] = self.request.user
        context['usuario_alvo'] = 'editar'
        user = get_object_or_404(User, username=self.request.user)

        # Obter o nome completo, e-mail e grupos
        context['nome_completo'] = f"{user.first_name} {user.last_name}"
        context['email'] = user.email
        context['grupo'] = user.groups.first().name
        context['grupo_primario'] = context['grupo']
        print(context)
        # Adicione outras variáveis de contexto conforme necessário
        return context

    def get(self, request, *args, **kwargs):
        current_dict = self.get_context_data()
        return render(request, self.current_page, current_dict)

    def post(self, request, *args, **kwargs):
        current_dict = self.get_context_data()
        if request.POST.get('adicionar'):
            current_dict['usuario_alvo'] = 'adicionar'
            current_dict['nome_usuario'] = ""
            current_dict['nome_completo'] = ""
            current_dict['email'] = ""
            current_dict['grupo_new'] = ""
            current_dict['grupo_primario'] = "usuario"
        if request.POST.get('acao_botao_usuarios'):
            if request.POST.get('acao_botao_usuarios') == 'adicionar':
                print(request.POST.dict())
                current_dict['erro_msg'] = self.validar_formato_senha(request.POST.get('senha'))
                if current_dict['erro_msg'] is None:
                    erro_msg = self.add_user(request.POST.dict(), atualizar=False)
                    print("AQUI")
                    current_dict = self.get_context_data()
                    current_dict['erro_msg'] = erro_msg
            if request.POST.get('acao_botao_usuarios') == 'editar_atual':
                erro_msg = self.add_user(request.POST.dict(), atualizar=True)
                current_dict = self.get_context_data()
                current_dict['erro_msg'] = erro_msg

            if request.POST.get('acao_botao_usuarios') == 'editar_outro':
                print(request.POST.dict())
                erro_msg = self.add_user(request.POST.dict(), atualizar=True)
                current_dict = self.get_context_data()
                current_dict['erro_msg'] = erro_msg
        
        if request.POST.get('nome_editar'):
            usuario = request.POST.get('nome_editar')
            infos = self.obter_informacoes_usuario_por_login(usuario)
            current_dict['usuario_alvo'] = 'editar_outro'
            current_dict['nome_usuario'] = usuario
            current_dict['nome_completo'] = f"{infos['primeiro_nome']} {infos['ultimo_nome']}"
            current_dict['email'] = infos['email']
            current_dict['grupo_primario'] =  infos['grupo_primario']
            current_dict['usuarios_editar'] = usuario
            
            print(usuario)

        if request.POST.get('excluir_usuario'):
            login = request.POST.get('login')
            print(login, "TESTE")
            print(request.POST.dict())
            try:
                # Tente encontrar o usuário pelo login
                usuario = User.objects.get(username=login)

                # Exclua o usuário
                usuario.delete()
                erro_msg = ""

            #except User.DoesNotExist:  
            except Exception as e:  
                erro_msg = "Usuário não existe"
            finally:
                current_dict = self.get_context_data()
                current_dict['erro_msg'] = erro_msg
                
        return render(request, self.current_page, current_dict)

    def add_user(self, request_data, atualizar=False):
        # Extraindo informações do dicionário
        login = request_data.get('login')
        nome = request_data.get('nome')
        grupo = request_data.get('grupo')
        email = request_data.get('email')
        senha = request_data.get('senha')

        try:
            # Verificar se o usuário já existe
            if User.objects.filter(username=login).exists():
                if atualizar:
                    # Tente obter o usuário pelo login
                    usuario = User.objects.get(username=login)
                    # Atualize os dados do usuário
                    usuario.username = login
                    if len(nome.split(' ')) > 1:
                        usuario.first_name = str(nome.split(' ')[0]).strip()
                        usuario.last_name = str(" ".join(nome.split(' ')[1:])).strip()
                    else:
                        usuario.first_name = str(nome).strip()
                        usuario.last_name = ''.strip()
                    usuario.email = email

                    if senha == "0000000000":
                        pass
                    else:
                        
                        usuario.set_password(senha)  # Certifique-se de usar set_password para armazenar a senha criptografada

                    # Atualize o grupo do usuário
                    usuario.groups.clear()  # Remove o usuário de todos os grupos anteriores
                    novo_grupo, criado = Group.objects.get_or_create(name=grupo)
                    usuario.groups.add(novo_grupo)

                    # Salve as alterações
                    usuario.save()
                    # Faça login novamente com as novas credenciais
                    user_atual = get_object_or_404(User, username=self.request.user)
                    if usuario == user_atual: 
                        djandoLogin(self.request, usuario)

                else:
                    return "Usuário já existe"


            elif atualizar is False:
                # Criar o usuário
                user = User.objects.create_user(username=login, password=senha, email=email, first_name=nome)
    
                # Adicionar o usuário ao grupo (se o grupo existir)
                novo_grupo, criado = Group.objects.get_or_create(name=grupo)
                user.groups.add(novo_grupo)

            return ''
        except Exception as e:
            print(e)
            return e
    def obter_informacoes_usuario_por_login(self ,login):
        try:
            # Tente obter o usuário pelo login
            usuario = User.objects.get(username=login)
    
            # Se o usuário for encontrado, você pode acessar as informações
            primeiro_nome = usuario.first_name
            ultimo_nome = usuario.last_name
            email = usuario.email
    
            # Obtenha o primeiro grupo do usuário, se existir
            primeiro_grupo = usuario.groups.first().name if usuario.groups.exists() else None
    
            # Agora você pode usar as informações como necessário
            return {
                'primeiro_nome': primeiro_nome,
                'ultimo_nome': ultimo_nome,
                'email': email,
                'grupo_primario': primeiro_grupo,
            }

        except User.DoesNotExist:
            # Lidere com o caso em que o usuário não existe
            return None



    def validar_formato_senha(self, senha):
            """
            Verifica a compatibilidade e critérios de formato da senha.
            Retorna uma mensagem de erro se houver algum problema, caso contrário, retorna None.
            """

            # Verificar se a senha atende aos critérios de formato
            if len(senha) < 8:
                return "A senha muito curta, ao menos 8."

            # Verificar se a senha atende aos critérios de formato
            if not re.search(r'[A-Z]', senha):
                return "A senha precisa de ao menos 1 caracter maiúsculo."

            # A senha atende aos critérios e é compatível
            return None
