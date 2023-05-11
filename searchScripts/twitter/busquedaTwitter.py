from itertools import islice
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
from dotenv import load_dotenv
load_dotenv()
import os
import concurrent.futures
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from tqdm import tqdm
import networkx as nx

class busquedaTwitter:
    def __init__(self, username, n_tweets):
        self.username = username
        self.n_tweets = n_tweets

    def resultadoBusqueda(self):
        scrape = self.Scraping(self.username, self.n_tweets)
        dataframe = scrape.scrape()
        
        word = self.WordCloudGenerator()
        wordcloud = word.generar_wordcloud(dataframe['Text'])

        top = self.GrafoTopInteracciones(dataframe['Text'])
        grafoTop = top.contar_interacciones()

        senti = self.SentimentalAnalysis(dataframe[["Text","Url"]])
        sentimentalAnalysis = senti.analizarTweets()

        grafoCo = self.GrafoComunidad(dataframe['Text'])
        grafoComunidad = grafoCo.to_json()
        datosComunidad = grafoCo.analisis_grafo()

        loca = self.Localizaciones(dataframe)
        locations = loca.esquema_localizaciones()

        return {"wordcloud": wordcloud, "grafoTop": grafoTop, "sentimentalAnalysis": sentimentalAnalysis, "locations": locations, "grafoComunidad":grafoComunidad, "datosComunidad":datosComunidad}

    class Scraping:
        def __init__(self, username, n_tweets):
            self.username = username
            self.n_tweets = n_tweets

        def scrape(self):
            # Creating list to append tweet data to
            tweets_list1 = []
            # Using TwitterSearchScraper to scrape data and append tweets to list
            for i,tweet in tqdm(enumerate(sntwitter.TwitterProfileScraper(self.username).get_items()), desc= "Progreso Scraping: ", total=self.n_tweets):
                try:
                    if i>=self.n_tweets:
                        break
                    if not (tweet.rawContent).startswith("RT"):
                        tweets_list1.append([tweet.date, tweet.id, tweet.rawContent, tweet.url, tweet.place])
                except Exception:
                    pass
            # Creating a dataframe from the tweets list above 
            tweets_df1 = pd.DataFrame(tweets_list1, columns=['Datetime', 'Tweet Id', 'Text', 'Url', 'Location'])
            return tweets_df1

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
            print("Generando Wordcloud...")
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
            wordcloud = WordCloud(background_color="white", mask=mask_twitter, max_words=200, stopwords=self.stopwords, contour_width=0, contour_color='steelblue', scale=2, collocations=False)

            wordcloud.generate(texto_limpio)

            # Crear un archivo temporal para guardar la imagen
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                output_path = tmp.name

                # Guardar la imagen en el archivo temporal
                wordcloud.to_file(output_path)

                # Devolver la ruta de la imagen
                print("Wordcloud Generado")
                return output_path
    
    class GrafoTopInteracciones:
        def __init__(self, dataframe):
            self.dataframe = dataframe

        def contar_interacciones(self):
            interacciones = {}
            for _, row in tqdm(self.dataframe.items(),desc="Progreso Grafo TopInteracciones: ",total=len(self.dataframe)):
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
            print("Ordenando nodos interacciones...")
            topInteracciones = sorted(interacciones.items(), key=lambda x: x[1], reverse=True)[:31] #31 por si está el mismo en la lista, luego se elimina si lo está
            print("Nodos ordenados")
            return topInteracciones
    
    class GrafoComunidad:
        def __init__(self, dataframe):
            self.G = nx.Graph()
            self.dataframe = dataframe
            print("Creando Grafo Comunidad")
            self._create_graph()

        def contar_interacciones(self):
            interacciones = {}
            for _, row in self.dataframe.items():
                text = row
                menciones = re.findall(r'@(\w+)', text)
                if len(menciones) > 1:
                    for i in range(len(menciones)):
                        for j in range(i+1, len(menciones)):
                            usuario1 = menciones[i]
                            usuario2 = menciones[j]
                            if usuario1 not in interacciones:
                                interacciones[usuario1] = {}
                            if usuario2 not in interacciones[usuario1]:
                                interacciones[usuario1][usuario2] = 0
                            interacciones[usuario1][usuario2] += 1
            return interacciones


        def obtener_interacciones(self):
            # Obtener el diccionario de interacciones de los usuarios en el DataFrame
            interacciones = self.contar_interacciones()
            usuarios = interacciones.keys()
            interacciones_tuplas = [(u, interacciones[u]) for u in usuarios]
            return interacciones_tuplas

        def _create_graph(self):
            for user, interactions in self.obtener_interacciones():
                for other_user in interactions.keys():
                    self.G.add_edge(user, other_user)
                    
            # Get communities
            communities = nx.algorithms.community.greedy_modularity_communities(self.G)
            self.communities = list(communities)

        def to_json(self):
            # Convertir el grafo a un JSON compatible con Vis.js
            nodes = []
            edges = []
            color = ['red', 'blue', 'green', 'orange', 'purple', 'yellow', 'pink','cyan', 'magenta', 'black', 'grey']
            for i, community in enumerate(self.communities):
                for node in community:
                    nodes.append({'id': node,'label':node, 'color': color[i % len(color)]})
                    for neighbor in self.G.neighbors(node):
                        if neighbor in community and {'from': neighbor, 'to': node} not in edges:
                            edges.append({'from': node, 'to': neighbor})
            print("Grafo Comunidad generado")
            return {'nodes': nodes, 'edges': edges}

        def analisis_grafo(self):
            resultados = []
            color = ['Rojo', 'Azul', 'Verde', 'Naranja', 'Morado', 'Amarillo', 'Rosa','Cyan','Magenta', 'Negro', 'Gris']
            for i, componente in enumerate(self.communities):
                grafo_componente = self.G.subgraph(componente)
                analisis_componente = {}
                analisis_componente['color'] = color[i % len(color)]
                analisis_componente['densidad'] = nx.density(grafo_componente)
                analisis_componente['diametro'] = nx.diameter(grafo_componente)
                analisis_componente['excentricidad'] = nx.radius(grafo_componente)
                analisis_componente['centro'] = nx.center(grafo_componente)
                analisis_componente['grado_medio'] = sum(dict(nx.degree(grafo_componente)).values()) / float(len(componente))
                analisis_componente['clustering_medio'] = nx.average_clustering(grafo_componente)
                analisis_componente['cohesion'] = nx.algorithms.cuts.conductance(self.G, componente)
                betweeness = nx.algorithms.centrality.betweenness_centrality_subset(grafo_componente, targets=componente, sources=componente)
                # Obtener los 5 valores más grandes distintos de 0
                betweenness = {k: v for k, v in betweeness.items() if v > 0}
                top_five = dict(islice(sorted(betweenness.items(), key=lambda item: item[1], reverse=True), 5))

                # Construir un nuevo diccionario con los 5 valores más grandes en orden descendente
                analisis_componente['betweenness_comunidad'] = top_five

                # Agregar cálculo de periferia
                excentricidades = nx.eccentricity(grafo_componente)
                periferia = [nodo for nodo, excentricidad in excentricidades.items() if excentricidad == max(excentricidades.values())]
                analisis_componente['periferia'] = periferia

                resultados.append(analisis_componente)
            modularidad = nx.algorithms.community.modularity(self.G, self.communities)
            return modularidad, resultados
        
    class SentimentalAnalysis:
        def __init__(self, dataframe):
            # Inicialización de las variables necesarias
            self.modelo = "MilaNLProc/xlm-emo-t" # Nombre del modelo
            self.tokenizer = AutoTokenizer.from_pretrained(self.modelo) # Tokenizador del modelo
            self.device = "cuda" if torch.cuda.is_available() else "cpu" # Comprobar si GPU está disponible
            self.model = AutoModelForSequenceClassification.from_pretrained(self.modelo).to(self.device) # Modelo de clasificación de sentimientos
            self.dataframe = dataframe # Dataframe de tweets
            self.listaTweetsLink = self.dataframe.values.tolist() # Lista de tweets con su link
            self.emotions = self.model.config.id2label.values() # Lista de emociones del modelo

            self.tweets_with_top_emotion = {emotion: {'score': 0, 'tweet': '', 'link': ''} for emotion in self.emotions} # Diccionario que almacena los tweets con mayor puntuación de cada emoción


        def analizarTweet(self, tweet, link):
            # Procesamiento de un tweet
            inputs = self.tokenizer(tweet, return_tensors="pt").to(self.device) # Tokenización y envío del tweet al dispositivo disponible
            outputs = self.model(**inputs) # Clasificación del tweet
            logits = outputs.logits # Obtención de los logits, vectores con las predicciones en crudo que la clasificación del modelo genera, pero que aún necesita pasarle una función para normalizar dichos valores
            scores = torch.softmax(logits, dim=1).tolist()[0] # Cálculo de las probabilidades usando la función de softmax
            labels = self.model.config.id2label # Etiquetas de las emociones
            sentiment_result = [{'label': labels[i], 'score': scores[i]} for i in range(len(labels))] # Resultado de la clasificación del tweet

            top_sentiment = max(sentiment_result, key=lambda x: x['score']) # Obtener la emoción con la probabilidad más alta
            for emotion in self.emotions:
                if top_sentiment['label'] == emotion and top_sentiment['score'] > self.tweets_with_top_emotion[emotion]['score']:
                    self.tweets_with_top_emotion[emotion]['score'] = top_sentiment['score']
                    self.tweets_with_top_emotion[emotion]['tweet'] = tweet
                    self.tweets_with_top_emotion[emotion]['link'] = link
            #Los resultados de clasificacion son una tupla, la primera parte es el analisis de cada tweet con su emocion asignada, la segunda parte los tweets con el mayor score de las distintas emociones
            # return {'tweet': tweet, 'sentiment': top_sentiment['label'], 'sentiment_score': top_sentiment['score']}
            # Retornar los resultados de clasificación
            return top_sentiment['label']# Retornar los resultados de clasificación

        def analizarTweets(self):
            # Procesamiento de múltiples tweets
            tweets_analysis = [] # Lista de análisis de tweets
            with concurrent.futures.ThreadPoolExecutor() as executor: # Inicialización de los hilos
                futures = [] #lista de objetos futuros que representa el resultado de la funcion analizarTweet
                for tweet,link in self.listaTweetsLink:
                    futures.append(executor.submit(self.analizarTweet, tweet, link)) # Envío del tweet a la función de análisis de tweet,
                for future in tqdm(concurrent.futures.as_completed(futures), desc="Progreso Sentimental Analysis: ",total=len(futures)): # Uso de tqdm para crear la barra de progreso, tqdm recibe como argumento un iterador y le añade una barra de progreso. En este caso, el iterador es concurrent.futures.as_completed(futures), que es el iterador que devuelve los resultados de las tareas completadas a medida que se van terminando.
                    tweet_analysis = future.result() # Obtención de los resultados de análisis
                    tweets_analysis.append(tweet_analysis) # Añadir el resultado a la lista de análisis de tweets
                
            return tweets_analysis, self.tweets_with_top_emotion # Retornar los resultados de análisis de tweets y los tweets con mayor puntuación de cada emoción

    class Localizaciones:
        def __init__(self, dataframe):
            self.dataframe = dataframe
        #La variable data es una lista de diccionarios. Cada diccionario representa una fila de datos, y las claves del diccionario corresponden a los nombres de las 
        # columnas del DataFrame que se guardará en el archivo CSV. En este caso, las columnas son location, datetime y url.
        def esquema_localizaciones(self):
            self.dataframe['Location'] = self.dataframe['Location'].astype(str)
            df = self.dataframe.groupby('Location').agg({'Datetime': list, 'Url': list})
            data = [] 
            for index, group in tqdm(df.iterrows(), desc="Progreso Tabla Localizaciones: ",total=len(df.index)):
                #El objeto Place se guarda como string y solo queremos guardar el valor fullName="----", por tanto tendremos que usar la libreria re
                if index != "None":
                    location = re.search(r"fullName='(.+?)'", index).group(1)
                    map = re.search(r"name='(.+?)'", index).group(1)
                    data.append({
                        'location': location, 
                        'datetime': group['Datetime'],
                        'url': group['Url'],
                        'maps': f"https://www.google.com/maps/place/{map}",
                    })
            return data