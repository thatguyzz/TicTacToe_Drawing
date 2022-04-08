from shapely.geometry import LineString
from tkinter import *
import numpy as np
import time
import os


class main:
    # ==========================================================================================
    # ==========================================================================================
    #                                INICJALIZACJA
    # ==========================================================================================
    # ==========================================================================================

    def __init__(self,master):

        #zmienne potrzebne do GUI
        self.master = master
        self.color_fg = 'black'
        self.color_bg = 'white'
        self.old_x = None
        self.old_y = None
        self.penwidth = 3



        #zmienne potrzebne do logiki gry/ przechwytywania ruchów
        self.start_line = [0, 0]  # koordynaty początku ryszowania linii
        self.stop_line = [0, 0]  # koordynaty końca rysowania linii

        self.lines = []  # tablica dwuwymiarowa, zawiera historię indeksów narysowanych linii
        self.tmp_line = []  # tymczasowa tablica indeksów nadpisywana przy button-relase

        self.lines_count = 0  # pierwsze 4 kreski mają być liniami gry, więc liczymy kreski do 4 i wtedzy włączam możliwośc gry
        self.lines_coordinates = []  # tutaj będziemy zpaisywali koordynaty wszystkich linii (4)

        self.lines_intersections = []  # tutaj zapisujemy przecięcia linii, na podstawie których będziemy szukali punktów na matrycy
        self.lines_intersections_id = []  # tutaj zapisujemy id zidentyfikowanych punktów (tak, aby je pozniej spokojnie wybierać z tablicy i wiedzieć który jest gdzie)

        self.player_moves_coordinates = []  # tuataj zapisujemy koordynaty każdego ruchu
        self.average_point_player_move = []  # tutaj zapisujemy średnią z x i y koordynatów (punkt)
        self.count_X_lines = 0 #  zmienna potrzebna, by narysować przez gracza 2 kreski dla X

        self.X_or_O = 0  # flaga gracza, czy gra kółkiem czy krzyżykiem (kółko - 1; krzyżyk - 0)
        self.game_matrix = [0,0,0,
                            0,0,0,
                            0,0,0]  # macierz gry
        self.game_status = "in_game" #  status gry, potrzebny do sprawdzania, czy można rysować dalej
        self.X_0_buttons_available = True # ustawia dostępnośc wyboru (naciśnięcia) przycisków X/O

        # INICJALIZACJA GUI
        self.drawWidgets()


        # przechwytywanie eventów
        self.c.bind('<Button-1>',self.btn_down)  # przycisk myszy w dół
        self.c.bind('<B1-Motion>',self.paint) # przycisk wsiśnięty
        self.c.bind('<ButtonRelease-1>',self.reset)  # przycisk odciśnięty (zwolniony)






    # ==========================================================================================
    # ==========================================================================================
    #                                DRAWING LOGIC
    # ==========================================================================================
    # ==========================================================================================

    def btn_down(self,e):  # reakcja na  wciśnięcie

        self.X_0_buttons_available = False #  blokujemy przyciski wyboru X/O

        if self.game_status == "in_game":
            self.start_line = [e.x,e.y] #koordynaty po rozpoczęciu rysowania kreski
            self.player_moves_coordinates.append([e.x,e.y])  # wypełniamy tablicę koordynatów gracza (każdy punkt)(w tym przypadku tylko pierwszy, gdyż jest to btn_down)
            self.old_x = e.x  # koordynaty końca stają się koordynatami początku
            self.old_y = e.y

    def paint(self,e): #  pomiędzy wciśnięciem, a opuszczeniem przycisku
        if self.game_status == "in_game":
            if self.old_x and self.old_y:
                self.tmp_line.append(self.c.create_line(self.old_x,self.old_y,e.x,e.y,width=self.penwidth,fill=self.color_fg,capstyle=ROUND,smooth=True)) #  rysowanie
                #  to tak naprawdę tworzenie linii od starego punktu old_x_y do nowego e.x.y

                self.player_moves_coordinates.append([e.x, e.y])  # wypełniamy tablicę koordynatów gracza (każdy punkt)
            #zapisuję w tmp_line indeks początku linii


            self.old_x = e.x  # koordynaty końca stają się koordynatami początku
            self.old_y = e.y


    def reset(self,e):    #reseting or cleaning the canvas  #  reakcja na zwolnienie klawisza
        if self.game_status == "in_game":
            self.stop_line = [e.x,e.y] #zapisuję koordynaty końca linii
            self.old_x = None  # resetuję koordynaty, aby nie teorzyło dziwnej, długiej kreski na pół mapki
            self.old_y = None

            self.lines.append([min(self.tmp_line),max(self.tmp_line)]) #dodaję indeksy tymczasowe do historii linii
            self.tmp_line.clear() #czyszczę tablicę indeksów tymczasowych


            if self.lines_count<4:  # jeżeli liczba narysowanych linii jest mniejsza od 4, to znaczy, że siatka nie jest jeszcze stworzona
                self.c.create_line(self.start_line[0],self.start_line[1],self.stop_line[0],self.stop_line[1], width=5) #tworzy linie od początku rysowania do końca
                self.lines_count = self.lines_count + 1  # inkrementuję indeks
                self.lines_coordinates.append([self.start_line,self.stop_line])  # wypełniam teblicę koordynatów z końcami siatki
                self.clear_line()  # czyszczę ostatnią narysowaną krzywą, natomiast zostawiam prostą

                if self.lines_count == 3:
                    self.player_moves_coordinates.clear()

                if self.lines_count == 4:  # jeżeli siatka została narysowana, to jednorazowo (wciąż inkrementujemy indeks lines_count) wykrywamy punkty przecięcia siatki
                    try:  #  tutaj możemy otrzymać błędy, jeżeli gracz źle narysuje planszę
                        self.detect_intersection_points()

                        if self.X_or_O == 1: #  podpowiedź dla gracza, czym gra
                            self.status_label['text'] = 'Draw O'
                        else:
                            self.status_label['text'] = 'Draw X'

                    except ValueError:  #  jeżeli błędy występują, wyrzucam komunikat,  oraz po sekundzie czyszczę tablicę
                        self.status_label['text'] = "Draw again"

                        time.sleep(1)
                        self.clear()
                    except IndexError:
                        self.status_label['text'] = "Draw again"

                        time.sleep(1)
                        self.clear()

                    self.player_moves_coordinates.clear() #  czyszczę koordynaty linii, teraz będę używał zmiennej do zapisywanie i analizy ruchów gracza


            else:  # jeżeli już narysowaliśmy siatkę (liczba linii większa od 4)
                self.count_X_lines += 1
                if self.X_or_O == 1 or (self.count_X_lines == 2 and self.X_or_O == 0): #  waunek dla kółka (jedna linia); warunek dla krzyżyka - 2 linie
                    self.count_X_lines = 0
                    X = np.average([row[0] for row in self.player_moves_coordinates])
                    Y = np.average([row[1] for row in self.player_moves_coordinates])  # pobieramy średnie z koordynatów, które są naszym punktem gracza

                    self.average_point_player_move.append([X, Y])  # wypełniamy tablicę ruchów w.w. punktem

                    # r = 5
                    # x0 = X - r
                    # y0 = Y - r
                    # x1 = X + r
                    # y1 = Y + r
                    # self.c.create_oval(x0,y0,x1,y1, width=5, fill = 'green')

                    self.detect_player_position()  # algorytm wykrywania pozycji gracza oraz interpreacja matrycowa ORAZ algorytm ruchu komputera, wywołanie

                    self.player_moves_coordinates.clear()  # czyścimy poprzednie koordynaty

                    self.lines_count = self.lines_count + 1  # służy do zwiększenia iteracji, aby nie wchodziło powtórnie w warunek lines_count == 4


                    #  sprawdzamy wynik gry
                    self.game_status = self.game_check(self.game_matrix)

                    if self.game_status == "player":  #  wypełnianie tabelki informacyjnej
                        self.status_label['text'] = 'Player Won'

                    if self.game_status == "computer":  #  wypełnianie tabelki informacyjnej
                        self.status_label['text'] = 'Computer Won'

                    if self.game_status == "tie":  #  wypełnianie tabelki informacyjnej
                        self.status_label['text'] = 'Tie'

                    if self.game_status == "in_game":  #  wypełnianie tabelki informacyjnej
                        self.status_label['text'] = 'In game'





    # ==========================================================================================
    # ==========================================================================================
    #                                FUNKCJE WYKORZYSTYWANE PRZEZ PRZYCISKI
    # ==========================================================================================
    # ==========================================================================================



    def change_fg(self):  #changing the pen color
        self.color_fg=colorchooser.askcolor(color=self.color_fg)[1]

    def change_bg(self):  #changing the background color canvas
        self.color_bg=colorchooser.askcolor(color=self.color_bg)[1]
        self.c['bg'] = self.color_bg


    def clear(self):  # funkcja czyszcząca canvas (w menu)
        self.c.delete(ALL)  # usuwamy wszystko z obszaru canvas

        # czyścimy wszystkie zmienne
        self.start_line = [0, 0]
        self.stop_line = [0, 0]

        self.lines = []
        self.tmp_line = []

        self.lines_count = 0
        self.lines_coordinates = []

        self.lines_intersections = []
        self.lines_intersections_id = []

        self.player_moves_coordinates = []
        self.average_point_player_move = []
        self.count_X_lines = 0

        self.status_label['text'] = 'Choose X/O'

        self.game_matrix = [0, 0, 0,
                            0, 0, 0,
                            0, 0, 0]

        self.game_status = "in_game"
        self.X_0_buttons_available = True


    def clear_line(self):  # funkcja cofająca ruch
        try:
                line = self.lines[-1]  # przypisuję do zmienniej line ostatnią narysowaną kreskę
                for i in range(line[0],line[1]+1):  # line[0] oraz line[1] to ID kresek, dlatego usuwam je i zawartość pomiędzy nimi
                    self.c.delete(i)
                del self.lines[-1]  # usuwam ostatnia linijkę z historii
        except IndexError:
            print("No more lines to delete") # jeżeli nie ma już więcej lnijek do usunięcia

    def X_pressed(self): #  jeżeli nie jesteśmy w grze, przyciski się aktywują, możemy nimi dokonywać wyboeów
        if self.X_0_buttons_available == True:
            self.X.config(relief=SUNKEN)
            self.O.config(relief=RAISED)
            self.X_or_O = 0 #  krzyżyk



    def O_pressed(self):
        if self.X_0_buttons_available == True:
            self.O.config(relief=SUNKEN)
            self.X.config(relief=RAISED)
            self.X_or_O = 1 #  kółko


    # ==========================================================================================
    # ==========================================================================================
    #                                RYSOWANIE GUI
    # ==========================================================================================
    # ==========================================================================================

    def drawWidgets(self):  # tworzymy całe GUI
        self.controls = Frame(self.master,padx = 5,pady = 5)

        self.status_label = Label(self.controls, text="Choose X/O", font=('arial 18'),width=15,height=2) #  Tutaj wyświetlamy komunikaty
        self.status_label.grid(row=0, column=0, pady=30)

        self.X = Button(self.controls, text="X", font=('arial 18'), command=self.X_pressed) #  przycisk X
        self.X.grid(row=1,column=0)

        self.O = Button(self.controls, text="O", font=('arial 18'), command=self.O_pressed) #  przycisk O
        self.O.grid(row=1, column=1)

        self.X.config(relief=SUNKEN) #  jeżeli gracz nie wybrał X/O, to defaultowo jest krzyżyk


        self.controls.pack(side=LEFT)


        # self.Button_Undo = ttk.Button(self.master,text='Undo', command=self.clear_line)  #  przycisk wstecz
        # self.Button_Undo.pack(side=RIGHT, padx=15, pady=20)

        self.c = Canvas(self.master,width=700,height=600,bg=self.color_bg,)  # tworzymy Canvas
        self.c.pack(fill=BOTH,expand=True)

        menu = Menu(self.master)  # tworzymy Menu
        self.master.config(menu=menu)

        colormenu = Menu(menu)  # menu Color
        menu.add_cascade(label='Colors',menu=colormenu)
        colormenu.add_command(label='Brush Color',command=self.change_fg) #  submenu Brush Color
        colormenu.add_command(label='Background Color',command=self.change_bg) #  submenu Background Color

        optionmenu = Menu(menu)
        menu.add_cascade(label='Options',menu=optionmenu)  # menu options
        optionmenu.add_command(label='Restart Game',command=self.clear)  #  submenu Restart Game
        optionmenu.add_command(label='Exit',command=self.master.destroy)  #  submenu Exit



# ==========================================================================================
# ==========================================================================================
#                                DRAWING DETECTION LOGIC
# ==========================================================================================
# ==========================================================================================

    def detect_intersection_points(self): #  ta funkcja wyszukuje punktów przecięcia planszy, dzięki temu jesteśmy w stanie oszacować, gdzie gracz zagrał
        for line_1 in self.lines_coordinates:  #  iterujemy po każdej linii

            for line_2 in self.lines_coordinates: #  iterujemy po każdej linii

                if line_1 != line_2: #  jeżeli nie są to te same linie, to

                    lin1 = LineString(line_1) #  zmienne pomocnicze, aby móc skorzystać z funkcji intersection
                    lin2 = LineString(line_2)

                    intersection = lin1.intersection(lin2)  #  otrzymujemy punkt, lub jeżeli się nie przecinają, to nic

                    if intersection.is_empty != True: #  jeżeli sa przecięcia

                        point = intersection.coords[0] # pobieamy punkt
                        x = point[0]
                        y = point[1]

                        r = 5   # rysujemy małe punkty na przecięciach
                        x0 = x - r
                        y0 = y - r
                        x1 = x + r
                        y1 = y + r
                        self.c.create_oval(x0, y0, x1, y1, width=5, fill='red')

                        if point not in self.lines_intersections: #  punkty się duplikują, gdyż porównujemy te same kombinacje (tylko na odwrót),
                            self.lines_intersections.append(point) #  dzięki temu usuwamy je

        self.detect_intersection_points_id() #  teraz próbujemy zidentyfikować, który punkt gdzie leży, gdyż narazie mamy tylko informację o punktach



    def detect_intersection_points_id(self):

        #  oznaczenie ID wygląda następująco:
        #  1, 0, 3
        #  0, 0, 0
        #  4, 0 ,2

        sum_position = [] #  służy do szukania sum na X i Y danego przecięcia

        for x,y in self.lines_intersections:
            sum_position.append(x+y)

        point_1_id = sum_position.index(min(sum_position)) # punktowi z najmniejszą sumą dajemy ID 1, jak wyżej
        point_2_id = sum_position.index(max(sum_position)) # punktowi z największą sumą dajemy ID 2, jak wyżej


        tmp_lines_intersections = self.lines_intersections.copy() #  tworzymy tymczasową listę, aby poznać kolejne ID

        tmp_lines_intersections.remove(self.lines_intersections[point_1_id]) #  usuwamy wartości z tymczasowej listy
        tmp_lines_intersections.remove(self.lines_intersections[point_2_id])

        x_ref = -99999 #  tworzymy dwie wartości referencyjne - największą i najmniejszą
        y_ref = 99999
        for x,y in tmp_lines_intersections: #  szukamy w pozostałych dwóch punktach takiego, który ma większego X i mniejszego Y, czyli punkt 3

            if x_ref < x:
                x_ref = x

            if y_ref > y:
                y_ref = y

        point_3_id = sum_position.index(x_ref + y_ref) #  przypisujemy punkt 3
        tmp_lines_intersections.remove(self.lines_intersections[point_3_id])

        point_4 = tmp_lines_intersections[0] # mamy punkt 4

        point_4_id = sum_position.index(point_4[0] + point_4[1])

        self.lines_intersections_id.append(point_1_id) #  mamy indeksy wszystkich punktów w liście, możemy przejśc do wyszukiwania pozycji
        self.lines_intersections_id.append(point_2_id)
        self.lines_intersections_id.append(point_3_id)
        self.lines_intersections_id.append(point_4_id)


    def detect_player_position(self):
        point = self.average_point_player_move[-1] # wyciągamy ostatni ruch gracza (jego średnią)
        x = point[0] #  mamy X i Y teog punktu
        y = point[1]

        p_1 = self.lines_intersections[self.lines_intersections_id[0]] #  wyciągamy punkty przecięcia po id, których szukaliśmy wcześniej
        p_2 = self.lines_intersections[self.lines_intersections_id[1]]
        p_3 = self.lines_intersections[self.lines_intersections_id[2]]
        p_4 = self.lines_intersections[self.lines_intersections_id[3]]

        p_1_x = p_1[0] #  przypisujemy X i Y punktom
        p_1_y = p_1[1]

        p_2_x = p_2[0]
        p_2_y = p_2[1]

        p_3_x = p_3[0]
        p_3_y = p_3[1]

        p_4_x = p_4[0]
        p_4_y = p_4[1]

        # tworzymy macierze ruchów, z których będziemy korzystali (dla czytelności są one tak zapisane)
        area_1 = [1, 0, 0,
                  0, 0, 0,
                  0, 0, 0]

        area_2 = [0, 1, 0,
                  0, 0, 0,
                  0, 0, 0]

        area_3 = [0, 0, 1,
                  0, 0, 0,
                  0, 0, 0]

        area_4 = [0, 0, 0,
                  1, 0, 0,
                  0, 0, 0]

        area_5 = [0, 0, 0,
                  0, 1, 0,
                  0, 0, 0]

        area_6 = [0, 0, 0,
                  0, 0, 1,
                  0, 0, 0]

        area_7 = [0, 0, 0,
                  0, 0, 0,
                  1, 0, 0]

        area_8 = [0, 0, 0,
                  0, 0, 0,
                  0, 1, 0]

        area_9 = [0, 0, 0,
                  0, 0, 0,
                  0, 0, 1]

        is_move = None #  zmienna,

        if x < p_1_x and y < p_1_y:
            print(area_1)
            is_move = self.check_if_free(1, area_1)

        elif x > p_1_x and x < p_3_x and y < p_3_y:
            print(area_2)
            is_move = self.check_if_free(2, area_2)

        elif x > p_3_x and y < p_3_y:
            print(area_3)
            is_move = self.check_if_free(3, area_3)

        elif x < p_1_x and y > p_1_y and y < p_4_y:
            print(area_4)
            is_move = self.check_if_free(4, area_4)

        elif x > p_1_x and x < p_2_x and  y > p_1_y and y < p_2_y:
            print(area_5)
            is_move = self.check_if_free(5, area_5)

        elif x > p_3_x and y > p_3_y and y < p_2_y:
            print(area_6)
            is_move = self.check_if_free(6, area_6)

        elif x < p_4_x and y > p_4_y:
            print(area_7)
            is_move = self.check_if_free(7, area_7)

        elif x > p_4_x and x < p_2_x and y > p_4_y:
            print(area_8)
            is_move = self.check_if_free(8, area_8)

        elif x > p_2_x and y > p_2_y:
            print(area_9)
            is_move = self.check_if_free(9, area_9)

        if is_move == True:
            matrix_copy = np.array(self.game_matrix).tolist()
            computer_move = self.next_move(matrix_copy)
            self.draw(computer_move)


            #  wypełnianie planszy przez komputer
            if computer_move == 1:
                self.game_matrix = np.add(self.game_matrix, area_1)
                self.game_matrix = np.add(self.game_matrix, area_1)
            elif computer_move == 2:
                self.game_matrix = np.add(self.game_matrix, area_2)
                self.game_matrix = np.add(self.game_matrix, area_2)
            elif computer_move == 3:
                self.game_matrix = np.add(self.game_matrix, area_3)
                self.game_matrix = np.add(self.game_matrix, area_3)
            elif computer_move == 4:
                self.game_matrix = np.add(self.game_matrix, area_4)
                self.game_matrix = np.add(self.game_matrix, area_4)
            elif computer_move == 5:
                self.game_matrix = np.add(self.game_matrix, area_5)
                self.game_matrix = np.add(self.game_matrix, area_5)
            elif computer_move == 6:
                self.game_matrix = np.add(self.game_matrix, area_6)
                self.game_matrix = np.add(self.game_matrix, area_6)
            elif computer_move == 7:
                self.game_matrix = np.add(self.game_matrix, area_7)
                self.game_matrix = np.add(self.game_matrix, area_7)
            elif computer_move == 8:
                self.game_matrix = np.add(self.game_matrix, area_8)
                self.game_matrix = np.add(self.game_matrix, area_8)
            elif computer_move == 9:
                self.game_matrix = np.add(self.game_matrix, area_9)
                self.game_matrix = np.add(self.game_matrix, area_9)



    def draw(self, area_id):
        p_1 = self.lines_intersections[self.lines_intersections_id[0]]
        p_2 = self.lines_intersections[self.lines_intersections_id[1]]
        p_3 = self.lines_intersections[self.lines_intersections_id[2]]
        p_4 = self.lines_intersections[self.lines_intersections_id[3]]

        p_1_x = p_1[0]
        p_1_y = p_1[1]

        p_2_x = p_2[0]
        p_2_y = p_2[1]

        p_3_x = p_3[0]
        p_3_y = p_3[1]

        p_4_x = p_4[0]
        p_4_y = p_4[1]

        average_distance = ((p_3_x - p_1_x)/2 + (p_2_x - p_4_x)/2 + (p_4_y - p_1_y)/2 + (p_2_y - p_3_y)/2)/4
        r = average_distance/2

        if area_id == 1:
            x = p_1_x - average_distance
            y = p_1_y - average_distance

            self.draw_X_O(x, y, r)

        if area_id == 2:
            x = p_1_x + (p_3_x - p_1_x)/2
            y = (p_1_y + p_3_y)/2 - average_distance

            self.draw_X_O(x, y, r)

        if area_id == 3:
            x = p_3_x + average_distance
            y = p_3_y - average_distance

            self.draw_X_O(x, y, r)

        if area_id == 4:
            x = (p_1_x + p_4_x)/2 - average_distance
            y = (p_4_y - p_1_y)/2 + p_1_y

            self.draw_X_O(x, y, r)

        if area_id == 5:
            x = (p_1_x + p_3_x + p_4_x + p_2_x)/4
            y = (p_1_y + p_3_y + p_4_y + p_2_y)/4

            self.draw_X_O(x, y, r)

        if area_id == 6:
            x = (p_3_x + p_2_x)/2 + average_distance
            y = (p_3_y + p_2_y)/2

            self.draw_X_O(x, y, r)

        if area_id == 7:
            x = (p_1_x + p_4_x)/2 - average_distance
            y = (p_2_y + p_4_y)/2 + average_distance

            self.draw_X_O(x, y, r)

        if area_id == 8:
            x = (p_4_x + p_2_x) / 2
            y = (p_4_y + p_2_y) / 2 + average_distance

            self.draw_X_O(x, y, r)

        if area_id == 9:
            x = (p_3_x + p_2_x) / 2 + average_distance
            y = (p_4_y + p_2_y) / 2 + average_distance

            self.draw_X_O(x, y, r)


    def draw_X_O(self, X, Y, r):

        if self.X_or_O == 0:  # rysujemy kółko
            x0 = X - r
            y0 = Y - r
            x1 = X + r
            y1 = Y + r
            self.c.create_oval(x0, y0, x1, y1, width=5, fill='green')

        else:  # rysujemy krzyżyk
            r = r - 5
            x1 = X - r
            y1 = Y + r
            x2 = X + r
            y2 = Y - r

            x3 = X - r
            y3 = Y - r
            x4 = X + r
            y4 = Y + r

            self.c.create_line(x1, y1, x2, y2, fill='black', width=6)
            self.c.create_line(x3, y3, x4, y4, fill='black', width=6)

            self.c.create_line(x1, y1, x2, y2, fill='red', width=2)
            self.c.create_line(x3, y3, x4, y4, fill='red', width=2)


    def check_if_free(self, area_id, area):

        free = None

        if self.game_matrix[area_id-1] == 0:
            free = True
        else:
            free = False


        if free == True:
            self.game_matrix = np.add(self.game_matrix, area)
        else:
            if self.X_or_O == 0:
                self.clear_line()
                self.clear_line()
            else:
                self.clear_line()
            return False

        return True



# ==========================================================================================
# ==========================================================================================
#                                COMPUTER'S MOVE LOGIC
# ==========================================================================================
# ==========================================================================================

    #  funkcja sprawdzająca wygraną

    def game_check(self, board):  # 0 - empty;  1 - player;  2 - computer
        # dla gracza
        # horizontally
        if board[0] == 1 and board[1] == 1 and board[2] == 1:
            return 'player'
        elif board[3] == 1 and board[4] == 1 and board[5] == 1:
            return 'player'
        elif board[6] == 1 and board[7] == 1 and board[8] == 1:
            return 'player'

        # vertically
        elif board[0] == 1 and board[3] == 1 and board[6] == 1:
            return 'player'
        elif board[1] == 1 and board[4] == 1 and board[7] == 1:
            return 'player'
        elif board[2] == 1 and board[5] == 1 and board[8] == 1:
            return 'player'

        # cross
        elif board[0] == 1 and board[4] == 1 and board[8] == 1:
            return 'player'
        elif board[6] == 1 and board[4] == 1 and board[2] == 1:
            return 'player'

        # dla komputera
        # horizontally
        elif board[0] == 2 and board[1] == 2 and board[2] == 2:
            return 'computer'
        elif board[3] == 2 and board[4] == 2 and board[5] == 2:
            return 'computer'
        elif board[6] == 2 and board[7] == 2 and board[8] == 2:
            return 'computer'

        # vertically
        elif board[0] == 2 and board[3] == 2 and board[6] == 2:
            return 'computer'
        elif board[1] == 2 and board[4] == 2 and board[7] == 2:
            return 'computer'
        elif board[2] == 2 and board[5] == 2 and board[8] == 2:
            return 'computer'

        # cross
        elif board[0] == 2 and board[4] == 2 and board[8] == 2:
            return 'computer'
        elif board[6] == 2 and board[4] == 2 and board[2] == 2:
            return 'computer'

        # jeżeli nie ma juz zer na planszy to jest remis
        # tie
        if 0 not in board:
            return "tie"

        #  nie ma juz innych opcji, więc gra toczy się dalej
        else:
            return "in_game"

    #  następny ruch komputera
    def next_move(self, board):

        status = self.game_check(board)  # funkcja sprawdzająca status - wywołanie
        moves_boards = []  # macierze pochodne o poziom niżej
        moves_values = []  # wartości wagowe macierzy w.w.

        if status == 'in_game':  # jeżeli gra się nie skończyła to podchodzimy do ruchu

            for i in range(0,
                           9):  # iterujemy po planszy zaznaczając 2 w pustych polach, następnie wywołujemy minimaxa, który zwraca wartość i ją przypisujemy ruchowi
                if board[i] == 0:
                    board[i] = 2
                    copy_board = np.array(board).tolist()
                    moves_values.append(
                        self.minimax(copy_board, "player"))  # kolejnym rychem jest ruch gracza, stąd 'player'
                    moves_boards.append(i)
                    board[i] = 0

            best_score = max(moves_values)  # najwyższa wartość (najlepszy ruch)
            print(moves_values)
            best_move_id = moves_values.index(best_score)  # id najlepszego ruchu (nierandomizowane)

            #  best move randomize - gdy są duplikaty wartości ruchów (takie same wagi), to aby nie było nudno losujemy z tych wag
            duplicates_best_score_counter = 0
            for value in moves_values:  # liczymy duplikaty
                if value == best_score:
                    duplicates_best_score_counter += 1

            rand_best_move_id = np.random.randint(0, duplicates_best_score_counter + 1)  # losujemy id
            if rand_best_move_id == 0:  # jeżeli jest równe 0, to zmieniamy na 1 (jak jest 1 wartość, to nie da się losować, stąd ten warunek)
                rand_best_move_id = 1

            duplicates_best_score_counter = 0  # znowu liczymy duplikaty
            move_id = 0  # ale teraz też liczymy id całego zbioru
            for value in moves_values:
                move_id += 1  # dodajemy, żeby wiedzieć, które zaznaczyć pole
                if value == best_score:
                    duplicates_best_score_counter += 1  # tutaj tak samo
                if duplicates_best_score_counter == rand_best_move_id:  # jeżeli się zgadzają indeksy z wylosowanym to wypisujemy
                    # print(move_id)

                    #  Interpreter na id planszy
                    counter = 0
                    zero_counter = 0
                    for move in board:
                        counter += 1

                        if move == 0:
                            zero_counter += 1

                        if zero_counter == move_id:
                            break

                    print(counter)
                    return counter


            # print(best_move_id+1)

        else:  # jeżeli się skończyła to wypisujemy rezultat
            print(status)

    # funkcja rekurencyjna, argumenty to tablica oraz tura (player/computer)
    def minimax(self, board, turn):
        moves_values = []  # wartości pod ruchów (drzewka)
        status = self.game_check(board)  # status gry sprawdzamy

        if status == 'in_game':  # jeżeli w danej macierzy nie została rozstrzygnięta gra to przystępujemy do algorytmu min max

            if turn == "computer":  # jeżeli tura komputera to maksymalizujemy wynik, gdyż komputer chce grać jak najlepiej

                for i in range(0, 9):  # iteracja po macierzy jak wcześniej, wypełniamy kolejne drzewka
                    if board[i] == 0:
                        board[i] = 2
                        copy_board = np.array(board).tolist()
                        moves_values.append(self.minimax(copy_board,
                                                    'player'))  # wywołanie rekurencyjne minimaksa z argumentem tury następnej (po komputerze - gracz)
                        board[i] = 0

                value = max(moves_values)  # maksymalizujemy wartośc zwracaną
                return value

            if turn == "player":  # jeżeli tura graca to minimalizujemy wynik, gdyż gracz chce grać jak najlepiej (najmniej korzystneie dla komputera)

                for i in range(0, 9):  # iteracja po macierzy jak wcześniej, wypełniamy kolejne drzewka
                    if board[i] == 0:
                        board[i] = 1
                        copy_board = np.array(board).tolist()
                        moves_values.append(self.minimax(copy_board,
                                                    'computer'))  # wywołanie rekurencyjne minimaksa z argumentem tury następnej (po graczu - komputer)
                        board[i] = 0

                value = min(moves_values)  # minimalizujemy wartośc zwracaną
                return value

        #  zakończenie drzewek gry
        if status == 'computer':  # dla komoutera dodantnie
            return 100

        elif status == "player":  # dla gracza ujemne
            return -100

        elif status == 'tie':  # za remis zero
            return 0


    # ==========================================================================================
    # ==========================================================================================
    #                                MAIN, FUNKCJA WYWOŁUJĄCA
    # ==========================================================================================
    # ==========================================================================================

if __name__ == '__main__':
    root = Tk()
    main(root)
    root.title('Tic Tac Toe')
    root.iconbitmap(os.path.join(os.path.dirname(__file__), "tictactoeicon.ico"))
    root.mainloop()

    













    
