from fpdf import FPDF

class PDF(FPDF):
    pdf_w = 210
    pdf_h = 297

    def Titles(self, compName):
        self.set_xy(5, 5)
        self.set_font("DejaVu", '', 16)
        self.cell(w=self.pdf_w-10, h=16, align='C', ln=2,
                  txt=compName, border=0)
        self.set_font("DejaVu", '', 12)
        self.cell(w=self.pdf_w-10, h=8, align='C',
                  txt="Протокол соревнований", border='B')

    def Teams(self, teams):
        self.set_xy(10, 32)
        self.set_font("DejaVu", '', 14)
        self.cell(w=100, h=10, align='L', border=0, ln=2, txt='Команды участницы:')
        self.set_font("DejaVu", '', 12)

        self.cell(w=70, h=8, ln=0, align='C', border='BTRL', txt="Название")
        self.cell(w=50, h=8, ln=0, align='C', border='BTR', txt="Время регистрации")
        self.cell(w=70, h=8, ln=1, align='C', border='BTR', txt='Представитель')
        for team in teams:
            self.cell(w=70, h=8, ln=0, align='C', border='RL', txt=team['name'])
            self.cell(w=50, h=8, ln=0, align='C', border='R', txt=team['registeredTime'])
            self.cell(w=70, h=8, ln=1, align='C', border='R', txt=team['user'])
        self.cell(w=190, h=0, ln=1, border='T', txt='')

    def Matches(self, matches):
        self.set_font("DejaVu", '', 14)
        self.cell(w=100, h=10, align='L', border=0, ln=2, txt='Матчи:')
        self.set_font("DejaVu", '', 12)

        self.cell(w=40, h=8, ln=0, align='C', border='BTRL', txt="Время")
        self.cell(w=40, h=8, ln=0, align='C', border='BTRL', txt="Место")
        self.cell(w=55, h=8, ln=0, align='C', border='BTR', txt="Победитель")
        self.cell(w=55, h=8, ln=1, align='C', border='BTR', txt='Проигравший')
        for match in matches:
            self.cell(w=40, h=8, ln=0, align='C', border='RL', txt=match['time'])
            self.cell(w=40, h=8, ln=0, align='C', border='RL', txt=match['place'])
            self.cell(w=45, h=8, ln=0, align='C', border='R', txt=match['winner'])
            self.set_fill_color(0, 200, 50)
            self.cell(w=10, h=8, ln=0, align='C', border='R', txt=match['winScore'], fill=True)
            self.cell(w=45, h=8, ln=0, align='C', border='R', txt=match['loser'])
            self.set_fill_color(230, 100, 100)
            self.cell(w=10, h=8, ln=1, align='C', border='R', txt=match['losScore'], fill=True)
        self.cell(w=190, h=0, ln=1, border='T', txt='')

    def OrganizerSignature(self, orginizerName, date):
        self.cell(w=150, h=15, ln=1)
        self.cell(w=80, h=10, align='R', border=0, ln=0, txt='Дата')
        self.set_font("DejaVu", '', 14)
        self.cell(w=110, h=10, align='R', ln=1, txt=date)
        self.set_font("DejaVu", '', 12)
        self.cell(w=80, h=10, align='R', ln=0, txt='Подпись организатора:')
        self.cell(w=80, h=10, align='R', ln=0, txt=orginizerName)
        self.cell(w=30, h=7, align='C', border="B", ln=1)

    def CompetitionProtocol(self, compName, teams, matches, orgName, date):
        self.add_page()
        self.add_font('DejaVu', '', 'DejaVuSerif.ttf', uni=True)
        self.set_text_color(0,0,0)
        self.Titles(compName)
        self.Teams(teams)
        self.Matches(matches)
        self.OrganizerSignature(orgName, date)
        self.output("tempFile.pdf","F")
