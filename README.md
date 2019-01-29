# Catalog App

O Catalog app visa resolver o problema de catalogação de itens com a descrição. O app oferece controle de autenticação e autorização nas operações de criação, edição, atualização e deleção de registros. 

## Features do App

Por meio do app, o usuário pode criar categorias diversas a fim de catalogar itens. Cada categoria pode contemplar vários itens. Cada item catalogado contém uma descrição. O app também oferece uma API externa utilizando REST para consulta. 

## Authentication and Authorization

Os recursos do CRUD têm controle de autenticação e autorização.

Os seguintes recursos requerem autenticação:

- CREATE (Autenticação)
- READ (Não Requer)
- UPDATE (Autenticação e Autorização)
- DELETE (Autenticação e Autorização)

Os usuários apenas estão aptos a atualizarem ou deletarem os itens e categorias de sua autoria. Para visualizarem os registros, usuários não autenticados ou autenticados podem visualizar o conteúdo armazenado.

## JSON API

O Catalog app contem uma API padrão rest para consulta por terceiros. Abaixo, URLs da interface:

Substitua as TAGs com os dados necessários:

<address>: Endereço de host ou DNS
<port>: Porta do socket
<id_catalog>: ID do catálogo
<id_item>: ID do item de um dado catálogo

- Consulta do catálogo principal: http://<address>:<port>/catalog/JSON
- Consulta de itens por catálogo: http://<address>:<port>/catalog/<id_catalog>/items/JSON
- Consulta da descrição do item: http://<address>:<port>/catalog/<id_catalog>/items/<id_item>/JSON
    
### Example JSON API Format

http://localhost:8000/catalog.json/<item_name>

Returns the details of a given <item_name>

{
  "cat_id": 1,
  "description": "Long description",
  "id": 1,
  "name": "Stick"
}
http://localhost:8000/catalog.json/

Returns all Categories and Items from the database

[
  {
    "id": 1,
    "items": [
      {
        "cat_id": 1,
        "description": "Long description",
        "id": 1,
        "name": "Stick"
      },
      {
        "cat_id": 1,
        "description": "",
        "id": 4,
        "name": "Shinguards"
      }
    ],
    "name": "Soccer"
  },
  {
    "id": 4,
    "items": [],
    "name": "Frisbee"
  },
  {
    "id": 5,
    "items": [
      {
        "cat_id": 5,
        "description": "",
        "id": 2,
        "name": "Goggles"
      },
      {
        "cat_id": 5,
        "description": "",
        "id": 3,
        "name": "Snowboard"
      }
    ],
    "name": "Snowboarding"
  }
]


# Requirements and Installation (Only in English) by Udacity (Adjusted by Gustavo)


## Requirements

Para instalar o Catalog App, basta instalar os seguintes aplicativos descritos:

### VirtualBox

VirtualBox is the software that actually runs the VM. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Downloads)  Install the *platform package* for your operating system.  You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

**Ubuntu 14.04 Note:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a [reported bug](http://ubuntuforums.org/showthread.php?t=2227131), installing VirtualBox from the site may uninstall other software you need.

### Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.  [You can download it from vagrantup.com.](https://www.vagrantup.com/downloads) Install the version for your operating system.

**Windows Note:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

### Git

If you don't already have Git installed, [download Git from git-scm.com.](http://git-scm.com/downloads) Install the version for your operating system.

On Windows, Git will provide you with a Unix-style terminal and shell (Git Bash).  
(On Mac or Linux systems you can use the regular terminal program.)

Once installed on computer, clone the follow repository to store locally: <https://github.com/gugs/>



## Installing the Catalog App (Already Performed)

**WARNING: THE PROCEDURE BELLOW WAS PERFORMED ALREADY!**

Once it is up and running, type **vagrant ssh**. This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type **exit** at the shell prompt.  To turn the virtual machine off (without deleting anything), type **vagrant halt**. If you do this, you'll need to run **vagrant up** again before you can log into it.


Now that you have Vagrant up and running type **vagrant ssh** to log into your VM.  change to the /vagrant directory by typing **cd /vagrant**. This will take you to the shared folder between your virtual machine and host machine.

Type **ls** to ensure that you are inside the directory that contains project.py, database_setup.py, and two directories named 'templates' and 'static'

Now type **python database_setup.py** to initialize the database.

Type **python filldb.py** to populate the database with restaurants and menu items. (Optional)

Type **python project.py** to run the Flask web server. In your browser visit **http://localhost:5000** to view the restaurant menu app.  You should be able to view, add, edit, and delete menu items and restaurants.
