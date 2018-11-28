# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

try:
    import holidays
except ImportError as err:
    _logger.debug(err)

import calendar
import datetime

from odoo import models, fields, api


class Calendario(models.Model):

    #campi di sistema
    _name = 'fba.calendario'
    _rec_name = 'name'
    _order = 'name ASC'


    #campi di relazione
    cal_calendariofascia_ids = fields.One2many('fba.calendariofascia', 'calfas_calendario_id')

    #campi di contenuto
    name = fields.Char(required=True, size=25, string='Nome')
    
    # Indica se il calendario è utilizzato per gli operatori o un ambulatorio
    cal_tipo = fields.Selection([(1, 'Ambulatori'), (2, 'Operatori')], required=True, string='Tipo calendario')
    


class CalendarioFascia(models.Model):

    #campi di sistema
    _name = 'fba.calendariofascia'
    _rec_name = 'name'
    _order = 'calfas_giorno ASC'


    #campi di relazione
    calfas_calendario_id = fields.Many2one('fba.calendario')


    #campi di contenuto
    name                = fields.Char(required=True, size=25)
    calfas_giorno       = fields.Selection([(1, 'Lunedì'), (2, 'Martedì'), (3, 'Mercoledì'), (4, 'Giovedì'), (5, 'Venerdì'), (6, 'Sabato'), (7, 'Domenica')], required=True, string='Giorno settimana')
    calfas_from         = fields.Float(string='Dalle ore')
    calfas_to           = fields.Float(string='Alle ore')
    calfas_dataInizio   = fields.Date(string='Dal giorno')
    calfas_dataFine     = fields.Date(string='Al giorno')


class calendarioAmbulatorio(models.Model):

    #campi di sistema
    _name = 'fba.calendarioambulatorio'
    _rec_name = 'calambul_calendario_id'
    _order = 'calambul_dataInizioValidita ASC'

    #campi di relazione
    calambul_ambulatorio_id = fields.Many2one('fba.ambulatorio', string='Ambulatorio')
    calambul_calendario_id = fields.Many2one('fba.calendario', string='Calendario')

    #campi di contenuto
    calambul_dataInizioValidita = fields.Date(string='Dal giorno')
    calambul_dataFineValidita = fields.Date(string='Al giorno')

    #metodi
    @api.multi
    def create(self, vals):
    
        _logger.info("************ create calendarioAmbulatorio ***************")
        _logger.info('self: ' + str(self))
        _logger.info('vals: ' + str(vals))
    
        # Si richiama la funzione della classe base che crea il record. Viene ritornato il record creato
        res = super(calendarioAmbulatorio, self).create(vals)
    
        dictAmbCalendar = {}
        dictAmbCalendar['id'] = res.id
        dictAmbCalendar['calambul_ambulatorio_id'] = res.calambul_ambulatorio_id.id
        dictAmbCalendar['calambul_calendario_id'] = res.calambul_calendario_id.id
        dictAmbCalendar['calambul_dataInizioValidita'] = res.calambul_dataInizioValidita
        dictAmbCalendar['calambul_dataFineValidita'] = res.calambul_dataFineValidita
    
        # Calcolo delle fasce di disponibilità di questo calendario ambulatorio
        calcolaFasceDisponibilitaAmbulatori(dictAmbCalendar, res.env)
        
        return res

    @api.multi
    def unlink(self):
    
        _logger.info("************ deleted calendarioAmbulatorio ***************")
        _logger.info('self: ' + str(self))
    
        dictAmbCalendar = {}
        dictAmbCalendar['id'] = self.id
        dictAmbCalendar['calambul_ambulatorio_id'] = self.calambul_ambulatorio_id.id
        dictAmbCalendar['calambul_calendario_id'] = self.calambul_calendario_id.id
        dictAmbCalendar['calambul_dataInizioValidita'] = self.calambul_dataInizioValidita
        dictAmbCalendar['calambul_dataFineValidita'] = self.calambul_dataFineValidita
    
        # Calcolo delle fasce di disponibilità di questo calendario ambulatorio
        calcolaFasceDisponibilitaAmbulatori(dictAmbCalendar, self.env, True)
    
        return models.Model.unlink(self)
    
    @api.multi
    def write(self, vals):
    
        _logger.info("************ modified calendarioAmbulatorio ***************")
        _logger.info('self: ' + str(self))
        _logger.info('vals: ' + str(vals))
    
        res = super(calendarioAmbulatorio, self).write(vals)
    
        dictAmbCalendar = {}
        dictAmbCalendar['id'] = self.id
        dictAmbCalendar['calambul_ambulatorio_id'] = self.calambul_ambulatorio_id.id
        dictAmbCalendar['calambul_calendario_id'] = self.calambul_calendario_id.id
        dictAmbCalendar['calambul_dataInizioValidita'] = self.calambul_dataInizioValidita
        dictAmbCalendar['calambul_dataFineValidita'] = self.calambul_dataFineValidita
    
        # Calcolo delle fasce di disponibilità associate al calendario del professionista
        calcolaFasceDisponibilitaAmbulatori(dictAmbCalendar, self.env)
    
        return res

class calendarioProfessionista(models.Model):

    #campi di sistema
    _name = 'fba.calendarioprofessionista'
    _rec_name = 'calprofess_calendario_id'
    _order = 'calprofess_dataInizioValidita ASC'


    #campi di relazione
    calprofess_professionista_id = fields.Many2one('fba.professionista', string='Professionista')
    calprofess_calendario_id = fields.Many2one('fba.calendario', string='Calendario')


    #campi di contenuto
    calprofess_dataInizioValidita = fields.Date(string='Dal giorno')
    calprofess_dataFineValidita = fields.Date(string='Al giorno')


    #metodi
    @api.multi
    def create(self, vals):
    
        _logger.info("************ create calendarioProfessionista ***************")
        _logger.info('self: ' + str(self))
        _logger.info('vals: ' + str(vals))
    
        # Si richiama la funzione della classae base che crea il record. Viene ritornato il record creato
        res = super(calendarioProfessionista, self).create(vals)
    
        dictEmplCalendar = {}
        dictEmplCalendar['id'] = res.id
        dictEmplCalendar['calprofess_professionista_id'] = res.calprofess_professionista_id.id
        dictEmplCalendar['calprofess_calendario_id'] = res.calprofess_calendario_id.id
        dictEmplCalendar['calprofess_dataInizioValidita'] = res.calprofess_dataInizioValidita
        dictEmplCalendar['calprofess_dataFineValidita'] = res.calprofess_dataFineValidita
    
        # Calcolo delle fasce di disponibilità di questo calendario utente
        calcolaFasceDisponibilitaProfessionisti(dictEmplCalendar, res.env)
        
        return res
    
    @api.multi
    def unlink(self):
    
        _logger.info("************ deleted calendarioProfessionista ***************")
        _logger.info('self: ' + str(self))
    
        dictEmplCalendar = {}
        dictEmplCalendar['id'] = self.id
        dictEmplCalendar['calprofess_professionista_id'] = self.calprofess_professionista_id.id
        dictEmplCalendar['calprofess_calendario_id'] = self.calprofess_calendario_id.id
        dictEmplCalendar['calprofess_dataInizioValidita'] = self.calprofess_dataInizioValidita
        dictEmplCalendar['calprofess_dataFineValidita'] = self.calprofess_dataFineValidita
    
        # Calcolo delle fasce di disponibilità di questo calendario utente
        calcolaFasceDisponibilitaProfessionisti(dictEmplCalendar, self.env, True)
    
        return models.Model.unlink(self)
    
    @api.multi
    def write(self, vals):
    
        _logger.info("************ modified calendarioProfessionista ***************")
        _logger.info('self: ' + str(self))
        _logger.info('vals: ' + str(vals))
    
        res = super(calendarioProfessionista, self).write(vals)
    
        dictEmplCalendar = {}
        dictEmplCalendar['id'] = self.id
        dictEmplCalendar['calprofess_professionista_id'] = self.calprofess_professionista_id.id
        dictEmplCalendar['calprofess_calendario_id'] = self.calprofess_calendario_id.id
        dictEmplCalendar['calprofess_dataInizioValidita'] = self.calprofess_dataInizioValidita
        dictEmplCalendar['calprofess_dataFineValidita'] = self.calprofess_dataFineValidita
    
        # Calcolo delle fasce di disponibilità associate al calendario del professionista
        calcolaFasceDisponibilitaProfessionisti(dictEmplCalendar, self.env)
    
        return res

def calcolaFasceDisponibilitaAmbulatori(dictAmbCalendar, env, removeOnly = False):
    '''
    Funzione per il calcolo delle fasce di disponibilità dato un determinato calendario associato ad un ambulatorio.
    Se il calendario è rimosso allora si effettua solamente la cancellazione delle fasce di validità
    ''' 
    
    # Identificativo dell'ambulatorio
    ambulatorio_id = dictAmbCalendar['calambul_ambulatorio_id']

    # Identificativo del calendario
    calendario_id = dictAmbCalendar['calambul_calendario_id']

    # Recupero ed impostazione delle festività di calendario
    festivita = holidays.IT(years=2018)
    festivita.append({"2018-09-08": "Madonna delle grazie"})

    # Data di inizio per il calcolo delle fasce di calendario
    base_date = datetime.datetime.now()

    # Rimozione di tutte le fasce orarie disponibili per l'ambulatorio in questione. Non si rimuovono quelle che indicano appuntamenti, ferie, permessi
    env['fba.eventoambulatorio'].search([('eventoambulatorio_tipo', '=', 1), ('eventoambulatorio_calendarioambulatorio_id', '=', dictAmbCalendar['id']), ('eventoambulatorio_start', '>', base_date.strftime("%Y-%m-%d %I:%M:%S"))]).unlink()

    # Se il calendario è rimosso allora si effettua solamente la cancellazione delle fasce di validità, quindi non si prosegue
    if (removeOnly == False):

        # Ricerca delle fasce di calendario per il calendario associato all'ambulatorio
        fasce_calendario = env['fba.calendariofascia'].search_read([('calfas_calendario_id', '=', calendario_id)])
        
        # Costruzione delle disponibilità in base al calendario
        for fascia in fasce_calendario:
            
            #_logger.info('fascia: ' + str(fascia))
        
            # Giorno della settimana
            day_of_week = fascia['calfas_giorno']
        
            # Recupero ora e minuti inizio
            ora_init = int(fascia['calfas_from'])
            minuti_init = int((fascia['calfas_from'] - ora_init)*60)
        
            # Recupero ora e minuti fine
            ora_end = int(fascia['calfas_to'])
            minuti_end = int((fascia['calfas_to'] - ora_end)*60)
        
            # Data inizio
            data_inizio = fascia['calfas_dataInizio']
            data_fine = fascia['calfas_dataFine']
        
            day_to_evaluate = base_date
        
            # Se ora attuale maggiore dell'ora di inizio della fascia allora si parte dal giorno successivo
            if day_to_evaluate.hour > ora_init:
                day_to_evaluate = day_to_evaluate + datetime.timedelta(days = 1)
        
            day_to_evaluate = day_to_evaluate.replace(hour=0, minute=0,second=0,microsecond=0)
        
            # Ora si verifica, per sette giorni, se il giorno della settimana coincide con la fascia.
            # Successivamente si sommano sette giorni per replicare la disponibilità
            bFound = True
            while (day_to_evaluate.isoweekday() != day_of_week and bFound == True):
                
                day_to_evaluate += datetime.timedelta(days = 1)
        
                dateTimeDifference = day_to_evaluate - base_date
        
                if (dateTimeDifference.days > 8):
                    bFound = False
        
            # Trovato il primo giorno della settimana da tenere in considerazione
            if bFound:

                # Si pianificano i successivi 100 giorni
                while ((day_to_evaluate - base_date).days < 100):
        
                    # La data non deve essere una festività e deve rientrare tra la data inizio e fine della fascia
                    if (day_to_evaluate.strftime('%Y-%m-%d') not in festivita):
        
                        if ((dictAmbCalendar['calambul_dataInizioValidita'] == False or datetime.datetime.strptime(dictAmbCalendar['calambul_dataInizioValidita'], '%Y-%m-%d') <= day_to_evaluate) and
                            (dictAmbCalendar['calambul_dataFineValidita'] == False or datetime.datetime.strptime(dictAmbCalendar['calambul_dataFineValidita'], '%Y-%m-%d') >= day_to_evaluate) and
                            (data_inizio == False or datetime.datetime.strptime(data_inizio, '%Y-%m-%d') <= day_to_evaluate) and
                            (data_fine == False or datetime.datetime.strptime(data_fine, '%Y-%m-%d') >= day_to_evaluate)):
        
                            event = {}
                            event['name'] = 'Disponibile'
                            event['eventoambulatorio_start'] = day_to_evaluate.strftime('%Y-%m-%d ') + ('00' + str(ora_init))[-2:] + ':' + ('00' + str(minuti_init))[-2:] + ":00"
                            event['eventoambulatorio_allday'] = False
                            event['eventoambulatorio_stop'] = day_to_evaluate.strftime('%Y-%m-%d ') + ('00' + str(ora_end))[-2:] + ':' + ('00' + str(minuti_end))[-2:] + ":00"
                            event['eventoambulatorio_tipo'] = 1
                            event['eventoambulatorio_ambulatorio_id'] = ambulatorio_id
                            event['eventoambulatorio_calendarioambulatorio_id'] = dictAmbCalendar['id']
                            env['fba.eventoambulatorio'].create(event)
        
                    day_to_evaluate += datetime.timedelta(days = 7)
        
                    
    #_logger.info("***************************")

def calcolaFasceDisponibilitaProfessionisti(calendarioProfessionista, env, removeOnly = False, ferie_e_permessi_escluso = -1):
    '''
    Funzione per il calcolo delle fasce di disponibilità dato un determinato calendario associato ad un impiegato.
    Se il calendario è rimosso allora si effettua solamente la cancellazione delle fasce di validità
    ''' 

    #_logger.info('ferie_e_permessi_escluso: ' + str(ferie_e_permessi_escluso))
    
    # Identificativo del dipendente
    professionista_id = calendarioProfessionista['calprofess_professionista_id']

    # Identificativo del calendario
    calendario_id = calendarioProfessionista['calprofess_calendario_id']

    # Recupero ed impostazione delle festività di calendario
    festivita = holidays.IT(years=2018)
    festivita.append({"2018-09-08": "Madonna delle grazie"})

    # Verifica delle sovrapposizioni tra gli eventi di calendario e le ferie/permessi
    ferie_e_permessi = env['fba.evento'].search_read([('even_tipo', '=', 2), ('even_professionista_id', '=', professionista_id)])
    ferie_e_permessi.extend(env['fba.evento'].search_read([('even_tipo', '=', 3), ('even_professionista_id', '=', professionista_id)]))

    #_logger.info('ferie_e_permessi: ' + str(ferie_e_permessi))

    ferie_e_permessi = [s for s in ferie_e_permessi if s['id'] != ferie_e_permessi_escluso]

    #_logger.info('ferie_e_permessi1: ' + str(ferie_e_permessi))

    # Data di inizio per il calcolo delle fasce di calendario
    base_date = datetime.datetime.now()

    # Rimozione di tutte le fasce orarie disponibili per l'utente in questione. Non si rimuovono quelle che indicano appuntamenti, ferie, permessi
    env['fba.evento'].search([('even_tipo', '=', 1), ('even_calendarioProfessionista_id', '=', calendarioProfessionista['id']), ('even_start', '>', base_date.strftime("%Y-%m-%d %I:%M:%S"))]).unlink()

    # Se il calendario è rimosso allora si effettua solamente la cancellazione delle fasce di validità
    if (removeOnly == False):

        # Ricerca delle fasce di calendario per il calendario associato al dipendente
        fasce_calendario = env['fba.calendariofascia'].search_read([('calfas_calendario_id', '=', calendario_id)])
        
        #_logger.info('fasce_calendario: ' + str(fasce_calendario))

        # Costruzione delle disponibilità in base al calendario
        for fascia in fasce_calendario:
            
            #_logger.info('fascia: ' + str(fascia))
        
            # Giorno della settimana
            day_of_week = fascia['calfas_giorno']
        
            # Recupero ora e minuti inizio
            ora_init = int(fascia['calfas_from'])
            minuti_init = int((fascia['calfas_from'] - ora_init)*60)
        
            # Recupero ora e minuti fine
            ora_end = int(fascia['calfas_to'])
            minuti_end = int((fascia['calfas_to'] - ora_end)*60)
        
            # Data inizio
            data_inizio = fascia['calfas_dataInizio']
            data_fine = fascia['calfas_dataFine']
        
            #_logger.info(str(data_inizio))
            #_logger.info(str(data_fine))
        
            day_to_evaluate = base_date
        
            # Se ora attuale maggiore dell'ora di inizio della fascia allora si parte dal giorno successivo
            if day_to_evaluate.hour > ora_init:
                day_to_evaluate = day_to_evaluate + datetime.timedelta(days = 1)
        
            day_to_evaluate = day_to_evaluate.replace(hour=0, minute=0,second=0,microsecond=0)
        
            # Ora si verifica, per sette giorni, se il giorno della settimana coincide con la fascia.
            # Successivamente si sommano sette giorni per replicare la disponibilità
            bFound = True
            while (day_to_evaluate.isoweekday() != day_of_week and bFound == True):
                
                day_to_evaluate += datetime.timedelta(days = 1)
        
                dateTimeDifference = day_to_evaluate - base_date
        
                if (dateTimeDifference.days > 8):
                    bFound = False
        
            # Trovato il primo giorno della settimana da tenere in considerazione
            if bFound:

                # Si pianificano i successivi 100 giorni
                while ((day_to_evaluate - base_date).days < 100):
        
                    # La data non deve essere una festività e deve rientrare tra la data inizio e fine della fascia
                    if (day_to_evaluate.strftime('%Y-%m-%d') not in festivita):
        
                        if ((calendarioProfessionista['calprofess_dataInizioValidita'] == False or datetime.datetime.strptime(calendarioProfessionista['calprofess_dataInizioValidita'], '%Y-%m-%d') <= day_to_evaluate) and
                            (calendarioProfessionista['calprofess_dataFineValidita'] == False or datetime.datetime.strptime(calendarioProfessionista['calprofess_dataFineValidita'], '%Y-%m-%d') >= day_to_evaluate) and
                            (data_inizio == False or datetime.datetime.strptime(data_inizio, '%Y-%m-%d') <= day_to_evaluate) and
                            (data_fine == False or datetime.datetime.strptime(data_fine, '%Y-%m-%d') >= day_to_evaluate)):
        
                            event = {}
                            event['name'] = 'Disponibile'
                            event['even_start'] = day_to_evaluate.strftime('%Y-%m-%d ') + ('00' + str(ora_init))[-2:] + ':' + ('00' + str(minuti_init))[-2:] + ":00"
                            event['even_allday'] = False
                            event['even_stop'] = day_to_evaluate.strftime('%Y-%m-%d ') + ('00' + str(ora_end))[-2:] + ':' + ('00' + str(minuti_end))[-2:] + ":00"
                            event['even_tipo'] = 1
                            event['even_professionista_id'] = professionista_id
                            event['even_calendarioProfessionista_id'] = calendarioProfessionista['id']

                            inserisci = True
                            for fep in ferie_e_permessi:

                                # Situazione in cui ferie e permessi annullano completamente un evento
                                if fep['even_start'] <= event['even_start'] and fep['even_stop'] >= event['even_stop']:
                                    inserisci = False
                                    break

                                # Situazione in cui ferie e permessi accorciano la fine di un evento
                                if fep['even_start'] <= event['even_start'] and fep['even_stop'] >= event['even_start']:
                                    event['even_start'] = fep['even_stop']
                                    break

                                # Situazione in cui ferie e permessi accorciano l'inizio di un evento
                                if fep['even_start'] <= event['even_stop'] and fep['even_stop'] >= event['even_stop']:
                                    event['even_stop'] = fep['even_start']
                                    break

                                # Situazione in cui ferie e permessi spezzano un evento in due
                                if fep['even_start'] > event['even_start'] and fep['even_stop'] < event['even_stop']:
                                    
                                    event1 = {}
                                    event1['name'] = 'Disponibile'
                                    event1['even_start'] = event['even_start']
                                    event1['even_allday'] = False
                                    event1['even_stop'] = fep['even_start']
                                    event1['even_tipo'] = 1
                                    event1['even_professionista_id'] = professionista_id
                                    event1['even_calendarioProfessionista'] = calendarioProfessionista['id']

                                    env['fba.evento'].create(event1)

                                    event['even_start'] = fep['even_stop']

                                    break
                            
                            if inserisci:
                                env['fba.evento'].create(event)
        
                    day_to_evaluate += datetime.timedelta(days = 7)
        
                    
    #_logger.info("***************************")
