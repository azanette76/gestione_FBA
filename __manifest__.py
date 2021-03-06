# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Gestione FBA',
    'version' : '1.0',
    'summary': 'Gestione del planning di FBA ONLUS',

 	'installable': True,
    'application': True,

    'data': [

        'views/_demodata.xml',  
        'views/_libraries.xml', 
        'views/_menu.xml', 		  

        'security/fba_security.xml',
        'security/ir.model.access.csv',                
    	
    	'views/paziente.xml',				#fba.paziente, fba.gravita, fba.azienda, fba.distretto, fba.operatorepreferenziale
    	'views/progetto.xml',				#fba.progetto, fba.prestazione, fba.ambito, fba.servizio, fba.anagraficaprestazione
    	'views/professionista.xml',			#fba.professionista, fba.competenza
        'views/evento.xml', 				#fba.evento, fba.sede, fba.ambulatorio						
        'views/calendari.xml',				#fba.calendario, fba.calendario.professionista
        'views/appuntamento.xml',		    #fba.appuntamento

        
     	],

    'depends': ['base',
                'web',
    			'muk_web_preview_text',
    			'backend_theme',
                'contacts',
                'hr',
                'calendar',
                'web_timeline',
                ],


                
    'external_dependencies': {'python': ['pyodbc', 'holidays']},
  
}

