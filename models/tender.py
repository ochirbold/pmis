from odoo import models, fields, api
# PURCHASE_REQUISITION_STATES = [
#     ('draft', 'Draft'),
#     ('ongoing', 'Ongoing'),
#     ('in_progress', 'Confirmed'),
#     ('open', 'Bid Selection'),
#     ('done', 'Closed'),
#     ('cancel', 'Cancelled')
# ]
class TenderInvitation(models.Model):
  _name = 'tender.invitation'

  tender_id = fields.Char("Тендер")
  tender_name = fields.Many2one('project.project',string="Төслийн нэр",required=True)
  tender_description = fields.Char(string="Төслийн товч мэдээлэл",required=True)
  tender_date = fields.Date('Тендер огноо', default=fields.Date.today())
  tender_meet_date = fields.Date('Танилцах уулзалтын огноо')
  last_date = fields.Date('Материал хүлээн авах эцсийн огноо')
  date = fields.Date('Хүлээн авах огноо')
  open_date = fields.Date('Нээх огноо')
  hariuts = fields.Many2one('res.partner', string="Хариуцагч")
  address = fields.Char(string="Материал хүлээн авах хаяг")
  price = fields.Integer(string="Материал худалдан авах үнэ")
  payment = fields.Integer(string="Барьцаа төлбөр")
  currency = fields.Many2one('res.currency', string="Валют")

  work = fields.Integer(string="Нэгж ажлын хөлс")
  material = fields.Integer(string="Нэгж материалын зардал")
  equipment = fields.Integer(string="Нэгж тоног төхөөрөмжийн зардал")
  transportation = fields.Integer(string="Нэгж тээврийн зардал")
  other = fields.Integer(string="Бусад зардал")
  unit_amount = fields.Integer(string="Нэгж нийт зардал", compute="_get_unit")
  unit_sizes = fields.Char(string="Хэмжих нэгж")

  quantity = fields.Integer(string="Тоо хэмжээ")

  
  amount = fields.Integer(string="Нийт төсөв ", compute="_get_total")

  work2 = fields.Integer(string="Нэгж ажлын хөлс")
  material2 = fields.Integer(string="Нэгж материалын зардал")
  equipment2 = fields.Integer(string="Нэгж тоног төхөөрөмжийн зардал")
  transportation2 = fields.Integer(string="Нэгж тээврийн зардал")
  other2 = fields.Integer(string="Бусад зардал")
  quantity2 = fields.Integer(string="Тоо хэмжээ")
  amount2 = fields.Integer(string="Нийт төсөв", compute="_get_total2")
  unit_amount2 = fields.Integer(string="Нэгж нийт зардал", compute="_get_unit2")
  unit_size2 = fields.Selection([
             ('м', 'м'),
             ('м2', 'м2'),
             ('м3', 'м3'),
             ('ширхэг', 'ширхэг'),
             ('багц ком', 'багц ком'),
             ('кг', 'кг'),
             ('гр', 'гр'),
             ('тнн', 'тнн'),
              ],default='')

  # state = fields.Selection([
  #           ('concept', 'Concept'),
  #           ('started', 'Started'),
  #           ('progress', 'In progress'),
  #           ('finished', 'Done'),
  #           ],default='concept')

  shaardlaga_ids = fields.One2many('shaardlaga.ids','shaardlaga')
  
  isd = fields.Many2one('project.task', string="Ажилбар")
  notes = fields.Text(string="Тодорхойлолт")
  startday = fields.Date(string="Эхлэх өдөр")
  endday = fields.Date(string="Дуусах өдөр")

  @api.onchange('tender_name')
  def get_project_value(self):
    self.tender_description = self.tender_name.description

  @api.onchange('isd')
  def get_task_value(self):
    self.startday = self.isd.startdate
    self.endday = self.isd.enddate
    self.quantity = self.isd.plan_amount_m
    # self.unit_sizes = self.ids.unit_size

# энэ хэсэг код нь project-task-төсөв хэсгээс нэгж үнийг category_id.name-р авчирч ажлуулж 
# байгаа тул хэрвээ төсөвийн мөр нэмэх хэсгийн name солих үед алдаа гарах тул сольсон category_id.name
# доорх [нэгж ажлын хөлс,нэгж материал, нэгж т/төхөөрөмж, нэгж тээвэр,нэгж бусад ] name-н оронд сольно
    for budget in self.isd.budget_lines:
      if budget.category_id.name == 'нэгж ажлын хөлс':
        self.work = budget.plan_amount
      if budget.category_id.name == 'нэгж материал':
        self.material = budget.plan_amount
      if budget.category_id.name == 'нэгж т/төхөөрөмж':
        self.equipment = budget.plan_amount
      if budget.category_id.name == 'нэгж тээвэр':
        self.transportation = budget.plan_amount
      if budget.category_id.name == 'нэгж бусад':
        self.other = budget.plan_amount

  @api.model
  def create(self, vals):
			created_invitation = self.env['tender.selection'].sudo().create({
				'tender_invitation_id': self.ids,
				'tender_id': vals['tender_id'],
				'tender_name': vals['tender_name'],
				'tender_description': vals['tender_description'],
        'tender_date': vals['tender_date'],
        'tender_meet_date': vals['tender_meet_date'],
        'last_date': vals['last_date'],
        'date': vals['date'],
        'open_date': vals['open_date'],
        'address': vals['address'],
        'price': vals['price'],
        'isd': vals['isd'],
        'notes': vals['notes'],
        'startday': vals['startday'],
        'endday': vals['endday'],
        'work2': vals['work'],
        })

			context = dict(self.env.context, mail_create_nolog=True)

			result = super(TenderInvitation, self.with_context(context)).create(vals)

			return result

  @api.one
  def write(self, vals):
      result = super(TenderInvitation, self).write(vals)
      return result

      #niilber1

  @api.one 
  @api.depends('work', 'material', 'equipment', 'transportation', 'other', 'quantity')
  def _get_total(self):
    for i in self:
      i.amount = (i.work * i.quantity) + (i.material * i.quantity) + (i.equipment * i.quantity) + (i.transportation * i.quantity) + (i.other * i.quantity)

      #niilber2

  @api.one 
  @api.depends('work2', 'material2', 'equipment2', 'transportation2', 'other2', 'quantity2')
  def _get_total2(self):
    for i in self:
      i.amount2 = (i.work2 * i.quantity2) + (i.material2 * i.quantity2) + (i.equipment2 * i.quantity2) + (i.transportation2 * i.quantity2) + (i.other2 * i.quantity2)
    # niilber3
  @api.one
  @api.depends('work','material','equipment', 'transportation', 'other')
  def _get_unit(self):
    for i in self:
      i.unit_amount = i.work + i.material + i.equipment + i.transportation + i.other
    # niilber4
  @api.one
  @api.depends('work2','material2','equipment2', 'transportation2', 'other2')
  def _get_unit2(self):
    for i in self:
      i.unit_amount2 = i.work2 + i.material2 + i.equipment2 + i.transportation2 + i.other2


class Shaardlaga(models.Model):
  _name = "shaardlaga.ids"

  requirement = fields.Char(string='Шаардлага')
  discription = fields.Html(string="Тайлбар")
  shaardlaga = fields.Many2one('tender.invitation')

  # @api.model
  # def create(self, vals):
  #     created_shaardlaga = self.env['tender.requirement'].sudo().create({
  #       'tender_shaardlaga_ids': self.ids,
  #       'shaardlaga_ids': vals['requir_ids'],
  #        })

  #     context = dict(self.env.context, mail_create_nolog=True)

  #     result = super(Shaardlaga, self.with_context(context)).create(vals)

  #     return result

  # @api.one
  # def write(self, vals):
  #     result = super(Shaardlaga, self).write(vals)
  #     return result
  


class Selection(models.Model):
  _name = 'tender.selection'

  tender_id = fields.Char("Тендер", readonly="1")
  tender_name = fields.Many2one('project.project',string="Төслийн нэр",readonly="1")
  tender_description = fields.Text(string="Төслийн товч мэдээлэл",readonly="1")
  tender_date = fields.Date(string='Тендер огноо',readonly="1")
  tender_meet_date = fields.Date('Танилцах уулзалтын огноо',readonly="1")
  last_date = fields.Date('Материал хүлээн авах эцсийн огноо',readonly="1")
  date = fields.Date('Хүлээн авах огноо',readonly="1") 
  open_date = fields.Date('Нээх огноо',readonly="1")

  address = fields.Char(string="Материал хүлээн авах хаяг",readonly="1")
  price = fields.Integer(string="Материал худалдан авах үнэ",readonly="1")
  payment = fields.Integer(string="Барьцаа төлбөр",readonly="1")
  currency = fields.Many2one(string="Валют")


  isd = fields.Many2one('project.task', string="Ажилбар",readonly="1")
  notes = fields.Text(string="Тодорхойлолт",readonly="1")
  quantity = fields.Float(string="Тоо хэмжээ",readonly="1")
  startday = fields.Date(string="Эхлэх өдөр",readonly="1")
  endday = fields.Date(string="Дуусах өдөр",readonly="1")

  # state = fields.Selection([
  #           ('concept', 'Concept'),
  #           ('started', 'Started'),
  #           ('progress', 'In progress'),
  #           ('finished', 'Done'),
  #           ],default='concept')

  negj_ids = fields.Many2many('tender.negj','negj')
  
class TenderNegj(models.Model):
  _name = 'tender.negj'
  work = fields.Float(string="Нэгж ажлын хөлс")
  material = fields.Float(string="Нэгж материалын зардал")
  equipment = fields.Float(string="Нэгж тоног төхөөрөмжийн зардал")
  transportation = fields.Float(string="Нэгж тээврийн зардал")
  other = fields.Float(string="Бусад зардал")

  discription = fields.Char(string="Тайлбар")
  requirement = fields.Char(string="Шаардлага")
  yesorno = fields.Char(strins="Тийм/Үгүй")
  

  company=fields.Many2one('res.partner',string="Компани")

  negj = fields.Many2one('tender.selection')

  # costt_ids = fields.One2many('tender.cost','costt')
  requir_ids = fields.One2many('tender.requirement', 'requir')

# class TenderNegj(models.Model):
#   _name = 'tender.cost'

#   work = fields.Float(string="Нэгж ажлын хөлс")
#   material = fields.Float(string="Нэгж материалын зардал")
#   equipment = fields.Float(string="Нэгж тоног төхөөрөмжийн зардал")
#   transportation = fields.Float(string="Нэгж тээврийн зардал")
#   other = fields.Float(string="Бусад зардал")
#   amount = fields.Float(string="niiit")

#   costt = fields.Many2one('tender.negj')
  

  class TenderRequirement(models.Model):
    _name = 'tender.requirement'

    discription = fields.Char(string="Тайлбар")
    requirement = fields.Char(string="Шаардлага")
    yesorno = fields.Char(strins="Тийм/Үгүй")
    requir = fields.Many2one('tender.negj')
    test = fields.Many2one('shaardlaga.ids')


class Project_des(models.Model):
  _inherit ='project.project'
  description = fields.Char(string="Description")