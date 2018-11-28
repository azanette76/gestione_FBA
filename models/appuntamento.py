# -*- coding: utf-8 -*-


from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

from odoo.addons_custom.gestione_FBA.models.calendari import calcolaFasceDisponibilitaProfessionisti


class Appuntamento(models.Model):
    '''
    Appuntamento di calendario
    '''

    #campi di sistema
    _name = 'fba.appuntamento'
    _rec_name = 'name'
    _order = 'name ASC'

    #campi di contenuto
    name = fields.Char(size=25, string='Nome')

    # Descrizione appuntamento
    appuntamento_descrizione = fields.Char(size=255, string='Descrizione')

    # Ora inizio appuntamento
    appuntamento_start = fields.Datetime('Data e ora inizio', required=True, help="Data e ora inizio appuntamento")
    # Ora fine appuntamento
    appuntamento_stop = fields.Datetime('Data e ora fine', required=True, help="Data e ora fine appuntamento")
    # Durata dell'appuntamento
    appuntamento_duration = fields.Float('Duration', states={'done': [('readonly', True)]})  
    # Indica se l'appuntamento riguarda tutto il giorno  
    appuntamento_allday = fields.Boolean('All Day', states={'done': [('readonly', True)]}, default=False)

    #campi di relazione

    # Professionisti legati all'appuntamento
    appuntamento_professionisti_ids = fields.Many2many('fba.professionista', relation='professionisti_appuntamento_rel', column1='appuntamento_id', column2='professionista_id')

    @api.multi
    def write(self, vals):
    
        _logger.info("************ modified appuntamento ***************")
        _logger.info('self: ' + str(self))
        _logger.info('vals: ' + str(vals))

        # Lista degli operatori coinvolti nell'appuntamento, prima della modifica
        lsProfessionisti_old = self.appuntamento_professionisti_ids

        res = super(Appuntamento, self).write(vals)

        # Lista degli operatori coinvolti nell'appuntamento, dopo della modifica
        lsProfessionisti = self.appuntamento_professionisti_ids

        # Ricalcolo delle fasce di disponibilità, tenuto conto della modifica all'appuntamento
        for prof in [prof for prof in lsProfessionisti_old if prof not in lsProfessionisti]:

            # Rimozione di tutti gli eventi legati all'appuntamento ed al professionista che sono legati all'appuntamento
            self.env['fba.evento'].search([('even_appuntamento_id', '=', self.id), ('even_professionista_id', '=', prof.id)]).unlink()

            lsCalendarioProfessionista = self.env['fba.calendarioprofessionista'].search_read([('calprofess_professionista_id', '=', prof.id)])

            # Calcolo delle fasce di disponibilità associate al calendario del professionista
            for calendarioProfessionista in lsCalendarioProfessionista:
                
                dictEmplCalendar = {}
                dictEmplCalendar['id'] = calendarioProfessionista['id']
                dictEmplCalendar['calprofess_professionista_id'] = calendarioProfessionista['calprofess_professionista_id'][0]
                dictEmplCalendar['calprofess_calendario_id'] = calendarioProfessionista['calprofess_calendario_id'][0]
                dictEmplCalendar['calprofess_dataInizioValidita'] = calendarioProfessionista['calprofess_dataInizioValidita']
                dictEmplCalendar['calprofess_dataFineValidita'] = calendarioProfessionista['calprofess_dataFineValidita']
            
                calcolaFasceDisponibilitaProfessionisti(dictEmplCalendar, self.env)

        # Ricalcolo delle fasce di disponibilità, tenuto conto della modifica all'appuntamento
        for prof in lsProfessionisti:

            event = {}
            event['even_start'] = self.appuntamento_start
            event['even_allday'] = self.appuntamento_allday
            event['even_stop'] = self.appuntamento_stop

            # Aggiornamento di tutti gli eventi legati all'appuntamento ed al professionista
            self.env['fba.evento'].search([('even_appuntamento_id', '=', self.id), ('even_professionista_id', '=', prof.id)]).write(event)

            lsCalendarioProfessionista = self.env['fba.calendarioprofessionista'].search_read([('calprofess_professionista_id', '=', prof.id)])

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
    
        _logger.info("************ create appuntamento ***************")
        _logger.info('self: ' + str(self))
        _logger.info('vals: ' + str(vals))

        # Si richiama la funzione della classe base che crea il record. Viene ritornato il record creato
        res = super(Appuntamento, self).create(vals)

        lsProfessionisti = res.appuntamento_professionisti_ids
    
        # Ricalcolo delle fasce di disponibilità, tenuto conto della modifica all'appuntamento
        for prof in lsProfessionisti:

            # Creazione dell'evento per il professionista che identifica l'appuntamento
            event = {}
            event['name'] = 'Appuntamento'
            event['even_start'] = res.appuntamento_start
            event['even_allday'] = res.appuntamento_allday
            event['even_stop'] = res.appuntamento_stop
            event['even_tipo'] = 4
            event['even_professionista_id'] = prof.id
            event['even_appuntamento_id'] = res.id

            # Esecuzione della creazione evento
            self.env['fba.evento'].create(event)
            
            lsCalendarioProfessionista = self.env['fba.calendarioprofessionista'].search_read([('calprofess_professionista_id', '=', prof.id)])

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
    
        _logger.info("************ deleted appuntamento ***************")
        _logger.info('self: ' + str(self))

        # Rimozione di tutti gli eventi legati all'appuntamento che si sta rimuovendo
        self.env['fba.evento'].search([('even_appuntamento_id', '=', self.id)]).unlink()

        # Lista degli operatori coinvolti nell'appuntamento
        lsProfessionisti = self.appuntamento_professionisti_ids

        # Ricalcolo delle fasce di disponibilità, tenuto conto della modifica all'appuntamento
        for prof in lsProfessionisti:

            lsCalendarioProfessionista = self.env['fba.calendarioprofessionista'].search_read([('calprofess_professionista_id', '=', prof.id)])

            # Calcolo delle fasce di disponibilità associate al calendario del professionista
            for calendarioProfessionista in lsCalendarioProfessionista:
                
                dictEmplCalendar = {}
                dictEmplCalendar['id'] = calendarioProfessionista['id']
                dictEmplCalendar['calprofess_professionista_id'] = calendarioProfessionista['calprofess_professionista_id'][0]
                dictEmplCalendar['calprofess_calendario_id'] = calendarioProfessionista['calprofess_calendario_id'][0]
                dictEmplCalendar['calprofess_dataInizioValidita'] = calendarioProfessionista['calprofess_dataInizioValidita']
                dictEmplCalendar['calprofess_dataFineValidita'] = calendarioProfessionista['calprofess_dataFineValidita']
            
                calcolaFasceDisponibilitaProfessionisti(dictEmplCalendar, self.env)
    
        res = models.Model.unlink(self)
    
        return res