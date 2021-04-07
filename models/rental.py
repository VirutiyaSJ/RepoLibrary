# -*- coding: utf-8 -*-
import logging


from datetime import timedelta,datetime
from odoo import fields, models,api

_logger = logging.getLogger(__name__)


class Rentals(models.Model):
    _name = 'library.rental'
    _description = 'Book rental'
    _order = "rental_date desc,return_date desc"


    _logger.info('---Rental module test---------------------')
    
    customer_id = fields.Many2one('res.partner', string='Customer' ,
        domain=[('customer','=',True)],required=True)
       # domain=['&', ('is_author','!=',True),('is_publisher','!=' , True)] )

    copy_id = fields.Many2one('library.copy', string="Book Copy", domain=[('book_state', '=', 'available')], required=True)
    book_id = fields.Many2one('product.product', string='Book', domain=[('is_book', '=', True)], related='copy_id.book_id', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('rented', 'Rented'), ('returned', 'Returned'), ('lost', 'Lost')], default="draft")


    rental_date = fields.Date(default=fields.Date.context_today, required=True)
    return_date = fields.Date(required=True)


    customer_address = fields.Many2one('res.partner' ,compute='_compute_customer_address' ,store=True)
#    customer_address = fields.Text(compute='_compute_customer_address')

    customer_email = fields.Char(related='customer_id.email')
    customer_address_display = fields.Text(compute='_compute_customer_address_display')

    book_authors = fields.Many2many(related='copy_id.author_ids')
    book_edition_date = fields.Date(related='copy_id.edition_date')
    book_publisher = fields.Many2one(related='copy_id.publisher_id')
    book_author_names = fields.Char(compute = '_compute_book_author_names',string="Authors")


    late_return = fields.Boolean(string = "Is Late" ,default="False" , compute="_compute_late_return" , store=True)

    actual_return_date = fields.Date()

    comments = fields.Text(string="Comments");


    def action_confirm(self):
        for rec in self:
            rec.state = 'rented'
            rec.copy_id.book_state = 'rented'
            rec.add_fee('time')

    def add_fee(self, type):
        for rec in self:
            if type == 'time':
                price_id = self.env.ref('library.price_rent')
                delta_dates = fields.Date.from_string(rec.return_date) - fields.Date.from_string(rec.rental_date)
                amount = delta_dates.days * price_id.price / price_id.duration
            elif type == 'loss':
                price_id = self.env.ref('library.price_loss')
                amount = price_id.price
            else:
                return

            self.env['library.payment'].create({
                'customer_id': rec.customer_id.id,
                'date':        rec.rental_date,
                'amount':      - amount,
            })

    def action_return(self):
        for rec in self:
            rec.state = 'returned'
            rec.copy_id.book_state = 'available'

    def action_lost(self):
        for rec in self:
            rec.state = 'lost'
            rec.copy_id.book_state = 'lost'
            rec.add_fee('loss')
            logging.info ('library.rental - action lost ')
            #rec.copy_id.active = False
            book_copies =  rec.book_id.copy_ids
            copy_count = len(book_copies)
            lost_count = 0 
            logging.info ('library.rental - action lost %s ' %(str(copy_count)))
            for copy in book_copies:
                if copy.book_state == 'lost':
                    lost_count += 1
                    logging.info ('library.rental - action lost %s ' %(str(lost_count)))

            if(copy_count > 1 and (copy_count == lost_count)):
                logging.info ('library.rental - action lost - setting to false ')
                rec.copy_id.active = False


    @api.model
    def _cron_check_date(self):
        late_rentals = self.search([('state', '=', 'rented'), ('return_date', '<', fields.Date.today())])
        template_id = self.env.ref('library.mail_template_book_return')
        for rec in late_rentals:
            mail_id = template_id.send_mail(rec.id)


    @api.depends('book_id',"copy_id")
    def name_get(self):
        result = []
        for r in self:

            result.append((r.id, 'Rental : %s / %s - [  %s ] ' % (str(r.id), r.copy_id.name , r.copy_id.reference)))

        return result

    @api.depends('return_date','actual_return_date')
    def _compute_late_return(self):
        late_return_flag =  False
        for r in self:
            if not r.actual_return_date:
                if r.return_date :
                    #temp_return_date = r.return_date
                    if (r.return_date <= fields.Date.today()):
                        late_return_flag = True
            else:
                # actual_return_date = r.actual_return_date
                # return_date = r.return_date
                if (r.actual_return_date > r.return_date):
                    late_return_flag =  True
            r.late_return = late_return_flag


    @api.depends('book_authors')
    def _compute_book_author_names(self):
        for r in self:
            if not r.book_authors:
                r.book_author_names = ""
            else:
#                r.author_names = r.mapped('author_ids.name')
                result = r.mapped('book_authors.name')
                r.book_author_names = ", ".join(result)

    @api.depends('customer_id')
    def _compute_customer_address(self):
        logging.info('####### %s 1 ')

        for r in self:
            logging.info('####### %s 2 ')


            if r.customer_id:
                logging.info('####### %s' %(r.customer_id.address_get() ))
                r.customer_address = r.customer_id.address_get(['contact'])['contact'] 


    @api.depends('customer_id')
    def _compute_customer_address_display(self):
        self.customer_address_display = self.customer_id._display_address() #This ln of code is enough



'''
    @api.depends('addr_id')
    def _compute_addr(self) 
      	for rec in self:
            addr = [rec.addr_id.street, rec.addr_id.street2,
                rec.addr_id.city,
                   rec.addr_id.zip]
            self.customer_address = ', '.join(filter(bool, addr))

'''

