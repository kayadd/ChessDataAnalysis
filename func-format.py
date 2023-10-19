import lichess.api
from lichess.format import SINGLE_PGN
from stockfish import Stockfish
import chess


# Eine Funktion, die den Zentibauernverlust angibt.
def CPL(BestMove, PlayedMove):
    print(abs(BestMove - PlayedMove))
    return abs(BestMove - PlayedMove)


class Game:
    # Enthält die Variablendeklaration.
    if True:
        # Enthält die Spielernamen.
        WhiteUser = ""
        BlackUser = ""

        # Enthält den Zeitpunkt.
        UTCDate = ""
        UTCTime = ""

        # Enthält das Rating.
        BlackELO = 0
        WhiteELO = 0

        # Enthält die Ratingdifferenz.
        ELODif = 0

        # Enthält die Variante.
        Variant = ""

        # Enthält den Spieltyp
        Type = ""

        # Enthält die Time-Control.
        TC = ""

        # Enthält das Opening.
        Opening = ""

        # Enthält die Zugfolgen.
        Moves = []

        # Enthält die Anzahl der Züge.
        NumberOfMoves = 0

        # Enthält den Ausgang des Spiels.
        Result = ""

        # Enthält die Eloänderung für den Weißspieler.
        ELOChangeWhite = 0
        # Enthält die Eloänderung für den Schwarzspieler.
        ELOChangeBlack = 0

        # Enthält die Analyse der Zuge mit der Engine:
        Analysis = []

        # Enthält die Accuracy des Weißspielers
        WhiteAccuracy = 0

        # Enthält die Accuracy des Schwarzspielers
        BlackAccuracy = 0

    def __init__(self, p_pgn):
        """Initialisiert ein Objekt der Klasse Game."""
        # Teilt die Metadaten.
        pgn = p_pgn.split("\n")

        # Filtert alle leeren Listeneinträge heraus.
        pgn_r = []
        for i in range(len(pgn)):
            if pgn[i] != "":
                pgn_r.append(pgn[i])

        pgn = pgn_r

        # Initialisiert den Spieltyp.
        self.Type = pgn[0][8:-2]

        if "Rated" not in self.Type:
            # Initialisiert die Variante.
            self.Variant = pgn[10][10:-2]
            # Initialisiert die Eröffnung.
            self.Opening = pgn[12][6:-2]
            # Initialisiert die Zeitkontrolle.
            self.TC = pgn[11][14:-2]
            # Initialisiert die Zugfolge.
            self.Moves = pgn[14].split(" ")

        else:
            self.Variant = pgn[12][10:-2]
            # Initialisiert die Zeitkontrolle.
            self.TC = pgn[13][14:-2]
            # Initialisiert die Eröffnung.
            self.Opening = pgn[14][6:-2]

            # Enthält die Eloänderung für den Weißspieler.
            self.ELOChangeWhite = pgn[10][18:-2]
            # Enthält die Eloänderung für den Schwarzspieler.
            self.ELOChangeBlack = pgn[11][18:-2]

            # Initialisiert die Zugfolge.
            self.Moves = pgn[16].split(" ")

        # Setzt den Namen des Weißspielers.
        self.WhiteUser = pgn[3][8:-2]
        # Setzt den Namen des Schwarzspielers.
        self.BlackUser = pgn[4][8:-2]

        # Initialisiert das Datum des Spiels.
        self.UTCDate = pgn[6][10:-2]
        # Initialisiert die Zeit des Spiels.
        self.UTCTime = pgn[7][10:-2]

        # Initialisiert die Elo von Weiß.
        self.WhiteELO = int(pgn[8][11:-2])
        # Initialisiert die Elo von Schwarz.
        self.BlackELO = int(pgn[9][11:-2])

        # Initialisiert die Elodifferenz.
        self.ELODif = (self.WhiteELO-self.BlackELO)

        # Initialisiert das Ergebnis.
        self.Result = self.Moves[-1]

        # Formatiert die Züge.
        NewMoves = []

        board = chess.Board()

        for i in range(len(self.Moves)):
            try:
                if i % 3 != 0:
                    lMove = str(board.parse_san(self.Moves[i]))
                    board.push_san(lMove)
                    NewMoves.append(lMove)
            except chess.InvalidMoveError:
                pass

        self.Moves = NewMoves

        # Initialisiert die Anzahl der gesamten Züge.
        self.NumberOfMoves = int((len(self.Moves)))-1
        self.NumberOfMoves = int(self.NumberOfMoves/2) + self.NumberOfMoves % 2

        # Initialisiert die Analyse:
        self.Analysis = []

    def Analyze(self):
        """Fügt dem Schachspiel eine Analyse in Form eines ACPLs hinzu."""
        # Setzt den Pfad für die aktuelle Engine fest und setzt die Parameter auf die Suchtiefe 24 und den maximalen
        # RAM-Verbrauch auf 2,048 GB.
        stockfish = Stockfish(path=r"stockfish-windows-x86-64-modern\stockfish\stockfish-windows-x86-64-modern.exe",
                              depth=24, parameters={"Hash": 2048})

        # Setzt die Startposition.
        stockfish.set_position([self.Moves[0]])

        # Analysiert den ersten Zug und fügt den Wert in die Liste ein.
        Eval = stockfish.get_evaluation()
        self.Analysis.append(Eval["value"])

        # Analysiert die restlichen Züge.
        for i in range(self.NumberOfMoves-1):
            BestEval = stockfish.get_top_moves(1)
            stockfish.make_moves_from_current_position([self.Moves[i+1]])
            Eval = stockfish.get_evaluation()
            # Unterscheidet zwischen der Auswertung vom reinen Zentibauern und einer Position in der Schachmatt
            # existiert.
            try:
                BestEval = (BestEval[0]["Centipawn"])
            except KeyError:
                BestEval = BestEval[0]["Mate"]*600

            self.Analysis.append(CPL(BestEval, Eval["value"]))

        # Rechnet die Summe aller Zentibauern geteilt nach der Farbe zusammen aus und zählt die Anzahl aller Züge
        # für jede Seite zusammen.
        MoveCounterBlack = 0
        MoveCounterWhite = 0
        try:
            for i in range(len(self.Analysis)):
                if (i % 2) != 0:
                    self.BlackAccuracy += self.Analysis[i]
                    MoveCounterBlack += 1
                else:
                    self.WhiteAccuracy += self.Analysis[i]
                    MoveCounterWhite += 1
        except IndexError:
            pass

        # Setzt die Werte fest, nachdem der Durchschnitt zu einem Integerwert konvertiert wurde.
        self.WhiteAccuracy = (int(self.WhiteAccuracy / MoveCounterWhite))
        self.BlackAccuracy = int(self.BlackAccuracy/MoveCounterBlack)


G = lichess.api.user_games("WKLCHESS", format=SINGLE_PGN, max=1)
