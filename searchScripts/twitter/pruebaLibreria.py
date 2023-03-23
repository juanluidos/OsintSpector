# import os
# import requests
# import random
# import tweepy
# from tweepy import OAuthHandler

# # Configuracion de acceso con las credenciales
# client = tweepy.Client(bearer_token=os.getenv('TWITTER_BEARER_TOKEN'))

 
# # Listos para hacer la conexion con el API
# api = tweepy.API(client)

# def randomUserAgent(filename):
#     with open(filename) as f:
#         lines = f.readlines()

#     return random.choice(lines).replace("\n","")

# def make_request(url, target):
#     headers = {
#     'format': 'application/json',
#     'timeout': '2.5',
#     'User-Agent': randomUserAgent("utils/userAgentsList.txt"),
#     "Authorization": "Bearer {}".format(os.getenv('TWITTER_BEARER_TOKEN'))
#     }
#     return requests.request("GET", f"{url}{target}", headers=headers)

# def getID(url, target):
#     response = make_request(url, target)
#     print(response.status_code)

# getID("https://api.twitter.com/2/users/by/username/","juanluidos")

from collections import Counter, defaultdict
import itertools
import json
import os
import tempfile
import unicodedata
from unidecode import unidecode
from wordcloud import WordCloud, STOPWORDS
import re
import numpy as np
import snscrape.modules.twitter as sntwitter
import pandas as pd
from PIL import Image
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords


# # Creating list to append tweet data to
# tweets_list1 = []

# # Using TwitterSearchScraper to scrape data and append tweets to list
# for i,tweet in enumerate(sntwitter.TwitterSearchScraper('from:JotaroKullons').get_items()):
#     if i>=6000:
#         break
#     tweets_list1.append([tweet.date, tweet.id, tweet.rawContent, tweet.url, tweet.place])
    
# # Creating a dataframe from the tweets list above 
# tweets_df1 = pd.DataFrame(tweets_list1, columns=['Datetime', 'Tweet Id', 'Text', 'Url', 'Location'])

# # Save dataframe as csv file in the current folder
# tweets_df1.to_csv('pruebaTweetsScraping.csv', index = False, encoding='utf-8') # False: not include index


class WordCloudGenerator:
    def __init__(self):
        #WordCloud
        self.textos_limpiados = []
        self.stopwords = set(STOPWORDS)
        self.logo_twitter = np.array(Image.open(os.path.join('static', 'assets', 'twitter_logo.png')))
        
    def limpiar_texto(self, texto):

        # Eliminar menciones
        texto = re.sub(r'@[A-Za-z0-9_]+', '', texto)

        # Eliminar urls
        texto = re.sub(r'https?://[A-Za-z0-9./]+', '', texto)

        # Eliminar caracteres HTML mal formados
        texto = re.sub(r'&[a-z]+;', '', texto)

        # Eliminar palabras con números y unidades
        texto = re.sub(r'\b\d+\s*[a-zA-Z]+\b', '', texto)

        # Eliminar hashtags
        texto = re.sub(r'#([^\s]+)', r'\1', texto)

        # Eliminar signos de puntuación y números
        texto = re.sub('[^a-zA-ZáéíóúüÁÉÍÓÚÜñÑ]', ' ', texto)

        # Eliminar espacios extra y saltos de línea
        texto = re.sub(' +', ' ', texto).strip()

        # Eliminar stopwords en español y en inglés
        spanish_stopwords = set(stopwords.words('spanish'))
        english_stopwords = set(stopwords.words('english'))
        all_stopwords = spanish_stopwords.union(english_stopwords)
        
        # Agregar versiones normalizadas de stopwords originales
        for stopword in spanish_stopwords:
            all_stopwords.add(unidecode(stopword))
        for stopword in english_stopwords:
            all_stopwords.add(unidecode(stopword))
        
        # Eliminar stopwords y palabras de una sola letra
        texto_limpio = [word.lower() for word in nltk.word_tokenize(texto) if word.lower() not in all_stopwords and len(word) > 1]

        # Convertir a minúsculas y normalizar letras con acentos y diéresis
        texto_limpio = " ".join(texto_limpio)
        texto_limpio = unicodedata.normalize('NFKD', texto_limpio.lower()).encode('ASCII', 'ignore').decode('utf-8')

        return texto_limpio

    def generar_wordcloud(self, textos):
        # Cargar la imagen del logo de Twitter
        logo_twitter = Image.open('static/assets/twitter_logo.png')

        # Convertir la imagen a una máscara
        mask_twitter = np.array(logo_twitter)
        mask_twitter[mask_twitter.sum(axis=2) == 0] = 255

        texto_limpio = ""

        # Iterar sobre los textos y limpiarlos
        for texto in textos:
            texto_limpio += self.limpiar_texto(texto) + " "

        # Crear la instancia de la clase WordCloud
        wordcloud = WordCloud(background_color="white", mask=mask_twitter, max_words=200, stopwords=self.stopwords, contour_width=0, contour_color='steelblue', scale=1.5, collocations=False)

        wordcloud.generate(texto_limpio)

        # Crear un archivo temporal para guardar la imagen
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            output_path = tmp.name

            # Guardar la imagen en el archivo temporal
            wordcloud.to_file(output_path)

            # Devolver la ruta de la imagen
            return output_path

# Crear una instancia de WordCloudGenerator
wc_generator = WordCloudGenerator()
tweets_df1 = pd.read_csv("pruebaTweetsScraping.csv", sep=",")

import networkx as nx
import matplotlib.pyplot as plt
# El constructor __init__ crea un grafo vacío utilizando nx.Graph() y almacena el DataFrame de entrada en la variable self.dataframe. Luego, llama al método _create_graph() para construir el grafo de interacciones entre usuarios.
# El método contar_interacciones() cuenta las interacciones entre usuarios en el DataFrame y devuelve un diccionario con el conteo de las interacciones.
# El método obtener_interacciones() utiliza el método contar_interacciones() para obtener el conteo de las interacciones entre usuarios y devuelve una lista de tuplas, donde cada tupla contiene un usuario y su lista de interacciones.
# El método _create_graph() utiliza la lista de tuplas devuelta por obtener_interacciones() para construir un grafo dirigido, donde cada nodo representa un usuario y cada arista representa una interacción entre usuarios.
# El método show_graph_Spring() muestra el grafo utilizando el algoritmo de disposición de Spring. Este método asigna a cada comunidad un color distinto y dibuja el grafo con los nodos y las aristas correspondientes.
# El método show_graph_KamadaKawai() muestra el grafo utilizando el algoritmo de disposición de Kamada-Kawai. Al igual que el método anterior, asigna un color distinto a cada comunidad y dibuja el grafo con los nodos y las aristas correspondientes.

class CommunityGraph:
    def __init__(self, dataframe):
        self.G = nx.Graph()
        self.dataframe = dataframe
        self._create_graph()

    def contar_interacciones(self):
        interacciones = {}
        for _, row in self.dataframe.items():
            text = row
            # busca si el tweet contiene una mención a otro usuario
            menciones = re.findall(r'@(\w+)', text)
            if menciones:
                # agrega las interacciones a la lista de interacciones
                for mencion in menciones:
                    if mencion not in interacciones:
                        interacciones[mencion] = {}
                    for mencionado in menciones:
                        if mencionado != mencion:
                            if mencionado not in interacciones[mencion]:
                                interacciones[mencion][mencionado] = 1
                            else:
                                interacciones[mencion][mencionado] += 1
        return interacciones

    def obtener_interacciones(self):
        # Obtener el diccionario de interacciones de los usuarios en el DataFrame
        interacciones = self.contar_interacciones()
        print(interacciones)
        print("\n")
        usuarios = interacciones.keys()
        interacciones_tuplas = [(u, interacciones[u]) for u in usuarios]
        print(interacciones_tuplas)
        return interacciones_tuplas

    def _create_graph(self):
        for user, interactions in self.obtener_interacciones():
            for other_user in interactions.keys():
                self.G.add_edge(user, other_user)
                
        # Get communities
        communities = nx.algorithms.community.greedy_modularity_communities(self.G)
        self.communities = list(communities)

    def show_graph_Spring(self):
        pos = nx.spring_layout(self.G, seed=42)
        plt.figure(figsize=(12, 8))
        node_color = [0] * len(self.G.nodes())
        for i, community in enumerate(self.communities):
            for node in community:
                node_color[list(self.G.nodes()).index(node)] = i + 1
        nx.draw_networkx(self.G, pos=pos, node_color=node_color, cmap='tab20', with_labels=True, node_size=800)
        plt.show()

    def show_graph_KamadaKawai(self):
        pos = nx.kamada_kawai_layout(self.G)
        plt.figure(figsize=(12, 8))
        node_color = [0] * len(self.G.nodes())
        for i, community in enumerate(self.communities):
            for node in community:
                node_color[list(self.G.nodes()).index(node)] = i + 1
        nx.draw_networkx(self.G, pos=pos, node_color=node_color, cmap='tab20', with_labels=True, node_size=800)
        plt.show()

class CommunityGraph2:
    def __init__(self, dataframe):
        self.G = nx.Graph()
        self.dataframe = dataframe
        self._create_graph()

    def contar_interacciones(self):
        interacciones = {}
        for _, row in self.dataframe.items():
            text = row
            # busca si el tweet contiene una mención a otro usuario
            menciones = re.findall(r'@(\w+)', text)
            if menciones:
                # agrega las interacciones a la lista de interacciones
                for mencion in menciones:
                    if mencion not in interacciones:
                        interacciones[mencion] = {}
                    for mencionado in menciones:
                        if mencionado != mencion:
                            if mencionado not in interacciones[mencion]:
                                interacciones[mencion][mencionado] = 1
                            else:
                                interacciones[mencion][mencionado] += 1
                        else:
                            pass
        return interacciones

    def obtener_interacciones(self):
        # Obtener el diccionario de interacciones de los usuarios en el DataFrame
        interacciones = self.contar_interacciones()
        print(interacciones)
        print("\n")
        usuarios = interacciones.keys()
        interacciones_tuplas = [(u, interacciones[u]) for u in usuarios]
        print(interacciones_tuplas)
        return interacciones_tuplas

    def _create_graph(self):
        for user, interactions in self.obtener_interacciones():
            for other_user in interactions.keys():
                self.G.add_edge(user, other_user)
                
        # Get communities
        communities = nx.algorithms.community.greedy_modularity_communities(self.G)
        self.communities = list(communities)

    def show_graph_Spring(self):
        pos = nx.spring_layout(self.G, seed=42)
        plt.figure(figsize=(12, 8))
        node_color = [0] * len(self.G.nodes())
        for i, community in enumerate(self.communities):
            for node in community:
                node_color[list(self.G.nodes()).index(node)] = i + 1
        nx.draw_networkx(self.G, pos=pos, node_color=node_color, cmap='tab20', with_labels=True, node_size=800)
        plt.show()

    def show_graph_KamadaKawai(self):
        pos = nx.kamada_kawai_layout(self.G)
        plt.figure(figsize=(12, 8))
        node_color = [0] * len(self.G.nodes())
        for i, community in enumerate(self.communities):
            for node in community:
                node_color[list(self.G.nodes()).index(node)] = i + 1
        nx.draw_networkx(self.G, pos=pos, node_color=node_color, cmap='tab20', with_labels=True, node_size=800)
        plt.show()

# Crear una instancia de la clase CommunityGraph con el dataframe
my_graph = CommunityGraph2(tweets_df1["Text"])
my_graph.obtener_interacciones()

my_graph.show_graph_Spring()
my_graph.show_graph_KamadaKawai()


class GrafoTopInteracciones:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def contar_interacciones(self):
        interacciones = {}
        for _, row in self.dataframe.items():
            text = row
            # busca si el tweet contiene una mención a otro usuario
            menciones = re.findall(r'@(\w+)', text)
            if menciones:
                # agrega las interacciones a la lista de interacciones
                for mencion in menciones:
                    if mencion not in interacciones:
                        interacciones[mencion] = 1
                    else:
                        interacciones[mencion] +=1
        topInteracciones = sorted(interacciones.items(), key=lambda x: x[1], reverse=True)[:30]
        return topInteracciones
    
w = GrafoTopInteracciones(tweets_df1["Text"])

print(w.contar_interacciones())