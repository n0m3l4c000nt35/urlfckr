# URLFCKR

Herramienta para analizar el código fuente en busca de subdominios y urls relativas a la ingresada para ampliar el campo de búsqueda de nuevos subdominios.

## Instalación

Crear un entorno virtual

En Linux

```
python3 -m venv venv
source venv/bin/activate
```

En Windows

```
venv\Scripts\activate
```

```
pip install -r requirements.txt
```

## Uso

En Linux

```
python3 urlfckr.py -u http://vulnweb.com
```

En Windows

```
python urlfckr.py -u http://vulnweb.com
```
