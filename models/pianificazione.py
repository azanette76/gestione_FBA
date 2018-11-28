# -*- coding: utf-8 -*-


# PAZ = paziente
# GRAV = gravita
# AZIEND = azienda
# DISTR = distretto
# PROG = progetto
# PREST = prestazione
# SERV = servizio
# anaPREST = anagrafica_prestazione
# SEDE = sede
# AMBU = ambulatorio
# OPERPREF = operatorepreferenziale
# COMPET = competenza
# PROFESS = professionista
# EVEN = evento
# cal = calendario
# calfas = calendariofascia
# calPROFESS = calendarioprofessionista



from odoo import models, fields, api
import logging
from datetime import datetime
from pytz import timezone


class paziente(models.Model):


	#campi di sistema
	_inherits = {'res.partner': 'paz_partner_id'}
	_name = 'fba.paziente'
	_rec_name = 'paz_rec_name'
	_order = 'name ASC'


	#campi di relazione
	paz_partner_id = fields.Many2one('res.partner', ondelete='cascade')
	paz_gravita_id = fields.Many2one('fba.gravita')
	paz_azienda_id = fields.Many2one('fba.azienda')
	paz_distretto_id = fields.Many2one('fba.distretto')

	paz_progetti_ids = fields.One2many('fba.progetto', 'prog_paziente_id')
	paz_progetti_attuali_ids = fields.One2many('fba.progetto', 'prog_paziente_id', domain=[('active', '=', 'True')] )
	paz_progetti_archivio_ids = fields.One2many('fba.progetto', 'prog_paziente_id', domain=[('active', '!=', 'True')] )

	paz_prestazioni_ids = fields.One2many('fba.prestazione', 'prest_paziente_id')		# domain=[('prest_status', '=', 'attuale'),'&',('prest_n_dapianificare', '=', '0')] )
	paz_prestazioni_dafare_ids = fields.One2many('fba.prestazione', 'prest_paziente_id', domain=[('active', '=', 'True'),'&',('prest_n_dapianificare', '>', '0')] )

	paz_operatoripreferenziali_ids = fields.One2many('fba.operatorepreferenziale', 'operpref_paziente_id')


	#campi di contenuto
	paz_cf = fields.Char()
	paz_bool_nome_con_cf = fields.Boolean()
	paz_rec_name = fields.Char(compute='_compute_paz_rec_name')

	# Identificativo filemaker
	paz_fm_id = fields.Char(string="Identificativo File Maker")


	
	#metodi
	@api.depends('name', 'paz_cf')
	def _compute_paz_rec_name(self):
		for record in self :
			if record.paz_bool_nome_con_cf :
				record.paz_rec_name = str( record.name ) + ' - ' + str( record.paz_cf )
			else :
				record.paz_rec_name = str( record.name )	

	def import_pazienti_from_FileMaker(self):
	
		logging.info("Importazione anagrafica pazienti")

		try:
			connectionString = "Driver={FileMaker ODBC};Server=localhost;Database=Contatti;UID=Admin;PWD="
			connection = pyodbc.connect(connectionString)

			cursor = connection.cursor()

			rows = cursor.execute("select ChiavePrimaria, Nome, Cognome from Contatti")
			file = open('C:/testFM.txt', 'w')

			gravita = self.env['gsanitaria.gravita'].search([])
			
			for row in rows:
			
				pazienteex = self.env['fba.paziente'].search([('paz_fm_id', '=', row[0])])
				
				paziente = {}
				paziente['paz_cf'] = row[0][:8]
				paziente['paz_gravita_id'] = gravita[0].id
				paziente['paz_fm_id'] = row[0]
				paziente['name'] = str(row[2]) + ' ' + str(row[1])

				if (len(pazienteex) == 0):
					self.env['fba.paziente'].create(paziente)
				else:
					pazienteex.write(paziente)

				file.write(str(paziente))
				file.write(str(row)) 
				file.write('\n')
			
			file.close()
			connection.close()

		except pyodbc.Error as err:
			logging.warn(err)
		except Exception as err:
			logging.warn(err)




class gravita(models.Model):


	#campi di sistema
	_name = 'fba.gravita'
	_rec_name = 'name'
	_order = 'name ASC'


	#campi di relazione
	grav_pazienti_ids = fields.One2many('fba.paziente', 'paz_gravita_id')


	#campi di contenuto
	name = fields.Char(required=True)
	grav_indice = fields.Integer(required=True)

	#metodi

	


class azienda(models.Model):


	#campi di sistema
	_name = 'fba.azienda'
	_rec_name = 'name'
	_order = 'name ASC'


	#campi di relazione
	aziend_pazienti_ids = fields.One2many('fba.paziente', 'paz_azienda_id')
	aziend_distretti_ids = fields.One2many('fba.distretto', 'distr_azienda_id')


	#campi di contenuto
	name = fields.Char(required=True)


	
	#metodi





class distretto(models.Model):


	#campi di sistema
	_name = 'fba.distretto'
	_rec_name = 'name'
	_order = 'sequence ASC, name ASC'

	sequence = fields.Integer(default=100)


	#campi di relazione
	distr_pazienti_ids = fields.One2many('fba.paziente', 'paz_distretto_id')
	distr_azienda_id = fields.Many2one('fba.azienda', ondelete='cascade')


	#campi di contenuto
	name = fields.Char(required=True)


	
	#metodi





class progetto(models.Model):


	#campi di sistema
	_name = 'fba.progetto'
	_rec_name = 'name'
	_order = 'sequence ASC, name ASC'

	sequence = fields.Integer(default=100)
	active = fields.Boolean(default=True)

	#campi di relazione
	prog_paziente_id = fields.Many2one('fba.paziente', ondelete='cascade')
	prog_prestazioni_ids = fields.One2many('fba.prestazione', 'prest_progetto_id')

	#campi di contenuto
	name = fields.Char(required=True)

	prog_interventi_generici_autorizzati = fields.Integer()
	prog_codici_autorizzazioni = fields.Char()
	
	
	#metodi






class prestazione(models.Model):


	#campi di sistema
	_name = 'fba.prestazione'
	_rec_name = 'prest_anagraficaprestazione_id'
	_order = 'sequence ASC, prest_anagraficaprestazione_id ASC'

	sequence = fields.Integer(default=100)
	active = fields.Boolean(compute='_compute_active', store=True)


	#campi di relazione
	prest_anagraficaprestazione_id = fields.Many2one('fba.anagraficaprestazione', required=True)

	prest_progetto_id = fields.Many2one('fba.progetto', ondelete='cascade')
	prest_paziente_id = fields.Many2one('fba.paziente', compute='_compute_prest_paziente_id')
	prest_servizio_id = fields.Many2one('fba.servizio', compute='_compute_prest_servizio_id')
	prest_professionisti_ids = fields.Many2many('fba.professionista', relation='professionisti_prestazione_rel', column1='prestazione_id', column2='professionista_id')

	prest_durata = fields.Float(related='prest_anagraficaprestazione_id.anaprest_durata')
	prest_interventi = fields.Float(related='prest_anagraficaprestazione_id.anaprest_interventi', digits=(4,1))


	#campi di contenuto
	prest_descrizione = fields.Text()
	prest_note = fields.Text()
	
	prest_n_appuntamenti = fields.Integer(help="Ciao crepa!")
	prest_n_interventi = fields.Integer(compute='_compute_prest_n_interventi', store=True)

	prest_specifiche_autorizzate = fields.Integer()

	prest_n_pianificate = fields.Integer()
	prest_n_dapianificare = fields.Integer(compute='_compute_prest_n_dapianificare', store=True)

	

	
	#metodi
	@api.depends('prest_progetto_id.active')
	def _compute_active(self):
		for record in self :
			record.active = record.prest_progetto_id.active

	@api.depends('prest_progetto_id')
	def _compute_prest_paziente_id(self):
		for record in self :
			record.prest_paziente_id = record.prest_progetto_id.prog_paziente_id

	@api.depends('prest_anagraficaprestazione_id')
	def _compute_prest_servizio_id(self):
		for record in self :
			record.prest_servizio_id = record.prest_anagraficaprestazione_id.anaprest_servizio_id

	@api.depends('prest_n_appuntamenti', 'prest_n_pianificate')
	def _compute_prest_n_dapianificare(self):
		for record in self :
			record.prest_n_dapianificare = record.prest_n_appuntamenti - record.prest_n_pianificate

	@api.depends('prest_n_appuntamenti', 'prest_anagraficaprestazione_id.anaprest_interventi')
	def _compute_prest_n_interventi(self):
		for record in self :
			record.prest_n_interventi = record.prest_n_appuntamenti * record.prest_anagraficaprestazione_id.anaprest_interventi






class servizio(models.Model):


	#campi di sistema
	_name = 'fba.servizio'
	_rec_name = 'name'
	_order = 'name ASC'



	#campi di relazione
	serv_anagraficaprestazioni_ids = fields.One2many('fba.anagraficaprestazione', 'anaprest_servizio_id')


	#campi di contenuto
	name = fields.Char(required=True)

	
	#metodi





class anagraficaprestazione(models.Model):


	#campi di sistema
	_name = 'fba.anagraficaprestazione'
	_rec_name = 'name'
	_order = 'sequence ASC, name ASC'

	sequence = fields.Integer(default=100)


	#campi di relazione
	anaprest_prestazione_ids = fields.One2many('fba.prestazione', 'prest_anagraficaprestazione_id')
	anaprest_servizio_id = fields.Many2one('fba.servizio', ondelete='cascade')

	anaprest_professionisti_ids = fields.Many2many('fba.professionista', relation='professionisti_anagraficaprestazioni_rel', column1='anagraficaprestazione_id', column2='professionista_id')
	anaprest_sedi_ids = fields.Many2many('fba.sede', relation='anagraficaprestazioni_sedi_rel', column1='anagraficaprestazione_id', column2='sede_id')
	anaprest_ambulatori_ids = fields.Many2many('fba.ambulatorio', relation='anagraficaprestazioni_ambulatori_rel', column1='anagraficaprestazione_id', column2='ambulatorio_id')
	anaprest_operatoripreferenziali_ids = fields.One2many('fba.operatorepreferenziale', 'operpref_anagraficaprestazione_id')


	#campi di contenuto
	name = fields.Char(required=True)
	anaprest_durata = fields.Float()
	anaprest_interventi = fields.Float( digits=(4,1) )

	anaprest_n_professionisti = fields.Integer()

	
	#metodi




class sede(models.Model):


	#campi di sistema
	_name = 'fba.sede'
	_rec_name = 'name'
	_order = 'name ASC'



	#campi di relazione
	sede_ambulatori_ids = fields.One2many('fba.ambulatorio', 'ambu_sede_id')
	sede_anagraficaprestazioni_ids = fields.Many2many('fba.anagraficaprestazione', relation='anagraficaprestazioni_sedi_rel', column1='sede_id', column2='anagraficaprestazione_id')




	#campi di contenuto
	name = fields.Char(required=True)

	
	#metodi





class ambulatorio(models.Model):


	#campi di sistema
	_name = 'fba.ambulatorio'
	_rec_name = 'name'
	_order = 'sequence ASC, name ASC'

	sequence = fields.Integer(default=100)
	ambu_nome_con_azienda = fields.Char(compute='_compute_ambu_nome_con_azienda')


	#campi di relazione
	ambu_sede_id = fields.Many2one('fba.sede', ondelete='cascade')
	ambu_anagraficaprestazioni_ids = fields.Many2many('fba.anagraficaprestazione', relation='anagraficaprestazioni_ambulatori_rel', column1='ambulatorio_id', column2='anagraficaprestazione_id')
	
	ambu_calendariambulatorio_ids = fields.One2many('fba.calendarioambulatorio', 'calambul_ambulatorio_id')

	#campi di contenuto
	name = fields.Char(required=True)

	
	#metodi
	@api.depends('name', 'ambu_sede_id.name')
	def _compute_ambu_nome_con_azienda(self):
		for record in self :
			record.ambu_nome_con_azienda = str( record.ambu_sede_id.name ) + ' - ' + record.name







class operatorepreferenziale(models.Model):


	#campi di sistema
	_name = 'fba.operatorepreferenziale'
	_rec_name = 'operpref_professionista_id'
	_order = 'operpref_professionista_id ASC'



	#campi di relazione
	operpref_paziente_id = fields.Many2one('fba.paziente', ondelete='cascade')
	operpref_professionista_id = fields.Many2one('fba.professionista', ondelete='cascade')
	operpref_anagraficaprestazione_id = fields.Many2one('fba.anagraficaprestazione', ondelete='cascade')


	#campi di contenuto
	

	
	#metodi







class competenza(models.Model):


	#campi di sistema
	_name = 'fba.competenza'
	_rec_name = 'name'
	_order = 'name ASC'



	#campi di relazione
	compet_professionisti_ids = fields.One2many('fba.professionista', 'profess_competenza_id')


	#campi di contenuto
	name = fields.Char(required=True)
	compet_indice = fields.Integer(required=True)

	
	#metodi






class professionista(models.Model):


	#campi di sistema
	_inherits = {'hr.employee': 'profess_employee_id'}
	_name = 'fba.professionista'
	_rec_name = 'profess_rec_name'
	_order = 'name ASC'



	#campi di relazione
	profess_employee_id = fields.Many2one('hr.employee', ondelete='cascade')
	profess_anagraficaprestazioni_ids = fields.Many2many('fba.anagraficaprestazione', relation='professionisti_anagraficaprestazioni_rel', column1='professionista_id', column2='anagraficaprestazione_id')
	profess_prestazioni_ids = fields.Many2many('fba.prestazione', relation='professionisti_prestazione_rel', column1='professionista_id', column2='prestazione_id')
	profess_competenza_id = fields.Many2one('fba.competenza')
	profess_operatoripreferenziali_ids = fields.One2many('fba.operatorepreferenziale', 'operpref_professionista_id')

	profess_calendariprofessionista_ids = fields.One2many('fba.calendarioprofessionista', 'calprofess_professionista_id')  # Lista dei calendari dell'utente
	profess_eventi_ids = fields.One2many('fba.evento', 'even_professionista_id')

	#campi di contenuto
	profess_cf = fields.Char()
	profess_bool_nome_con_cf = fields.Boolean()
	profess_rec_name = fields.Char(compute='_compute_profess_rec_name')


	
	#metodi
	@api.depends('name', 'profess_cf')
	def _compute_profess_rec_name(self):
		for record in self :
			if record.profess_bool_nome_con_cf :
				record.profess_rec_name = str( record.name ) + ' - ' + str( record.profess_cf )
			else :
				record.profess_rec_name = str( record.name )