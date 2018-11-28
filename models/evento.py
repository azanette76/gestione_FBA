# -*- coding: utf-8 -*-


from odoo import models, fields, api
import logging
from datetime import datetime
from pytz import timezone

from odoo.addons_custom.gestione_FBA.models.calendari import calcolaFasceDisponibilitaProfessionisti

_logger = logging.getLogger(__name__)


class EventoAmbulatorio(models.Model):
    '''
    Evento associato ad un ambulatorio
    '''

    #campi di sistema
    _name = 'fba.eventoambulatorio'
    _rec_name = 'name'
    _order = 'name ASC'

    #campi di relazione
    eventoambulatorio_ambulatorio_id = fields.Many2one('fba.ambulatorio')
    
    # Riferimento al calendario ambulatorio a cui è legato l'evento
    eventoambulatorio_calendarioambulatorio_id = fields.Many2one('fba.calendarioambulatorio')

    # riferimento all'appuntamento che genera l'evento
    eventoambulatorio_appuntamento_id = fields.Many2one('fba.appuntamento', string = 'Appuntamento')

    # Campi visibili dell'appuntamento associato all'evento
    eventoambulatorio_appuntamento_descrizione = fields.Char(related='eventoambulatorio_appuntamento_id.appuntamento_descrizione', readonly=True)

	#campi di contenuto
    name = fields.Char() # Nome dell'evento
    eventoambulatorio_descrizione = fields.Char()  # Descrizione dell'evento
    eventoambulatorio_tipo = fields.Selection([(1, 'Disponibile'), (4, 'Appuntamento')], required=True) # Tipologia di evento
    eventoambulatorio_start = fields.Datetime('Inizio', required=True, help="Start date of an event, without time for full days events") # Inizio evento 
    eventoambulatorio_stop = fields.Datetime('Fine', required=True, help="Stop date of an event, without time for full days events") # Fine evento
    eventoambulatorio_display_interval = fields.Char(compute = 'compute_eveneventoambulatorio_display_interval') # Stringa di visualizzazione dell'intervallo
    eventoambulatorio_allday = fields.Boolean('All Day', states={'done': [('readonly', True)]}, default=False)  # Indica se l'evento riguarda tutto il giorno  
    eventoambulatorio_duration = fields.Float('Duration', states={'done': [('readonly', True)]})  # Durata dell'evento

    #metodi
    @api.depends('eventoambulatorio_start')
    def compute_eveneventoambulatorio_display_interval(self):
        
        for rec in self:
        
            datetime_start = datetime
            datetime_stop = datetime
            
            datetime_start = datetime.strptime(rec.eventoambulatorio_start, '%Y-%m-%d %H:%M:%S')
            datetime_stop = datetime.strptime(rec.eventoambulatorio_stop, '%Y-%m-%d %H:%M:%S')
            
            diff = datetime_stop - datetime_start
            
            if rec.eventoambulatorio_tipo == 2:
                rec.eventoambulatorio_display_interval = 'Ferie'
            elif rec.eventoambulatorio_tipo == 3:
                rec.eventoambulatorio_display_interval = 'Permesso'
            else:
                if (datetime_start.date() == datetime_stop.date() or diff.total_seconds() <= 18000):
                    rec.eventoambulatorio_display_interval = datetime_start.strftime('%H:%M') + ' - ' + datetime_stop.strftime('%H:%M')

class Evento(models.Model):
    '''
    Evento associato ad un professionista
    '''

	#campi di sistema
    _name = 'fba.evento'
    _rec_name = 'name'
    _order = 'name ASC'

    #campi di relazione
    even_professionista_id = fields.Many2one('fba.professionista', string = 'Professionista')

    # Riferimento al calendario professionista legato all'evento
    even_calendarioProfessionista_id = fields.Many2one('fba.calendarioprofessionista')

    # riferimento all'appuntamento che genera l'evento
    even_appuntamento_id = fields.Many2one('fba.appuntamento', string='Dati appuntamento')

    # Campi visibili dell'appuntamento associato all'evento
    even_appuntamento_descrizione = fields.Char(related='even_appuntamento_id.appuntamento_descrizione', readonly=True)

	#campi di contenuto
    name = fields.Char(string = 'Nome') # Nome dell'evento
    even_descrizione = fields.Char(string = 'Descrizione')  # Descrizione dell'evento
    even_tipo = fields.Selection([(1, 'Disponibilità'), (2, 'Ferie'), (3, 'Permesso'), (4, 'Appuntamento')], required=True, string = 'Tipo') # Tipologia di evento
    even_start = fields.Datetime('Inizio', required=True, help="Start date of an event, without time for full days events") # Inizio evento 
    even_stop = fields.Datetime('Fine', required=True, help="Stop date of an event, without time for full days events") # Fine evento
    even_display_interval = fields.Char(compute = 'compute_even_display_interval') # Stringa di visualizzazione dell'intervallo
    even_allday = fields.Boolean('All Day', states={'done': [('readonly', True)]}, default=False)  # Indica se l'evento riguarda tutto il giorno  
    even_duration = fields.Float('Duration', states={'done': [('readonly', True)]})  # Durata dell'evento
   
   
    #metodi
    @api.depends('even_start')
    def compute_even_display_interval(self):
        
        for rec in self:
        
            datetime_start = datetime
            datetime_stop = datetime
            
            datetime_start = datetime.strptime(rec.even_start, '%Y-%m-%d %H:%M:%S')
            datetime_stop = datetime.strptime(rec.even_stop, '%Y-%m-%d %H:%M:%S')
            
            diff = datetime_stop - datetime_start
            
            if rec.even_tipo == 2:
                rec.even_display_interval = 'Ferie'
            elif rec.even_tipo == 3:
                rec.even_display_interval = 'Permesso'
            else:
                if (datetime_start.date() == datetime_stop.date() or diff.total_seconds() <= 18000):
                    rec.even_display_interval = datetime_start.strftime('%H:%M') + ' - ' + datetime_stop.strftime('%H:%M')

    @api.multi
    def write(self, vals):
    
        _logger.info("************ modified eventi ***************")
        _logger.info('self: ' + str(self))
        _logger.info('vals: ' + str(vals))
    
        res = super(Evento, self).write(vals)
    
        # Se l'evento creato è un permesso o delle ferie, allora si ricalcolano le disponibilità
        if (self.even_tipo == 2 or self.even_tipo == 3):
    
            # Ricerca dei calendari associati all'utente
            lsCalendarioProfessionista = self.env['fba.calendarioprofessionista'].search_read([('calprofess_professionista_id', '=', self.even_professionista_id.id)])
    
            # Calcolo delle fasce di disponibilità associate al calendario del professionista
            for calendarioProfessionista in lsCalendarioProfessionista:
                
                dictEmplCalendar = {}
                dictEmplCalendar['id'] = calendarioProfessionista['id']
                dictEmplCalendar['calprofess_professionista_id'] = calendarioProfessionista['calprofess_professionista_id'][0]
                dictEmplCalendar['calprofess_calendario_id'] = calendarioProfessionista['calprofess_calendario_id'][0]
                dictEmplCalendar['calprofess_dataInizioValidita'] = calendarioProfessionista['calprofess_dataInizioValidita']
                dictEmplCalendar['calprofess_dataFineValidita'] = calendarioProfessionista['calprofess_dataFineValidita']
    
                calcolaFasceDisponibilitaProfessionisti(dictEmplCalendar, self.env)
    
        return res
    
    @api.model
    def create(self, vals):
    
        _logger.info("************ create evento ***************")
        _logger.info('self: ' + str(self))
        _logger.info('vals: ' + str(vals))
    
        # Si richiama la funzione della classe base che crea il record. Viene ritornato il record creato
        res = super(Evento, self).create(vals)
    
        # Se l'evento creato è un permesso o delle ferie, allora si ricalcolano le disponibilità
        if (vals['even_tipo'] == 2 or vals['even_tipo'] == 3):
    
            # Ricerca dei calendari associati all'utente
            lsCalendarioProfessionista = self.env['fba.calendarioprofessionista'].search_read([('calprofess_professionista_id', '=', res.even_professionista_id.id)])
    
            # Calcolo delle fasce di disponibilità associate al calendario del professionista
            for calendarioProfessionista in lsCalendarioProfessionista:
                
                dictEmplCalendar = {}
                dictEmplCalendar['id'] = calendarioProfessionista['id']
                dictEmplCalendar['calprofess_professionista_id'] = calendarioProfessionista['calprofess_professionista_id'][0]
                dictEmplCalendar['calprofess_calendario_id'] = calendarioProfessionista['calprofess_calendario_id'][0]
                dictEmplCalendar['calprofess_dataInizioValidita'] = calendarioProfessionista['calprofess_dataInizioValidita']
                dictEmplCalendar['calprofess_dataFineValidita'] = calendarioProfessionista['calprofess_dataFineValidita']
    
                calcolaFasceDisponibilitaProfessionisti(dictEmplCalendar, self.env)
    
        return res
    
    
    @api.one
    def unlink(self):
    
        _logger.info("************ deleted evento ***************")
        _logger.info('self: ' + str(self))
    
        tipo = self.even_tipo
        env = self.env
        empid = self.even_professionista_id.id
    
        # Se l'evento creato è un permesso o delle ferie, allora si ricalcolano le disponibilità
        if (tipo == 2 or tipo == 3):
        
            # Ricerca dei calendari associati all'utente
            lsCalendarioProfessionista = env['fba.calendarioprofessionista'].search_read([('calprofess_professionista_id', '=', empid)])
        
            # Calcolo delle fasce di disponibilità associate al calendario del professionista
            for calendarioProfessionista in lsCalendarioProfessionista:
                
                dictEmplCalendar = {}
                dictEmplCalendar['id'] = calendarioProfessionista['id']
                dictEmplCalendar['calprofess_professionista_id'] = calendarioProfessionista['calprofess_professionista_id'][0]
                dictEmplCalendar['calprofess_calendario_id'] = calendarioProfessionista['calprofess_calendario_id'][0]
                dictEmplCalendar['calprofess_dataInizioValidita'] = calendarioProfessionista['calprofess_dataInizioValidita']
                dictEmplCalendar['calprofess_dataFineValidita'] = calendarioProfessionista['calprofess_dataFineValidita']
        
                calcolaFasceDisponibilitaProfessionisti(dictEmplCalendar, env, ferie_e_permessi_escluso = self.id)

        res = models.Model.unlink(self)
        #_logger.info('res: ' + str(res))
    
        return res