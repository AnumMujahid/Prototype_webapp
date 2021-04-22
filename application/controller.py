from flask import flash
from flask import current_app as app
from flask_login import login_user
from flask_sqlalchemy import sqlalchemy

from .model import *

from datetime import datetime


def login_(email, password):

    user = User.query.filter_by(email=email).first()
    if (user and user.check_password(password1=password)):
        login_user(user)
        flash(f'Welcome {user.username}', 'success')
        return True

    flash('Invalid username/password combination', 'danger')
    return False


def editplotprice_(plot_id, price):
    db.session.query(Plot).filter_by(id=plot_id).update({'price': price})
    db.session.commit()

    flash('Plot Price Successfully Edited', 'success')


### Buyer ###
def addbuyer_(buyer):
    try:
        buyer = Buyer(
            name=buyer['name'],
            cnic=buyer['cnic'],
            phone=buyer['phone'],
            email=buyer['email'],
            address=buyer['address'],
            cnic_front=buyer['cnic_front'],
            cnic_back=buyer['cnic_back'],
            comments=buyer['comments']
        )

        db.session.add(buyer)
        db.session.commit()

        flash(f'Buyer with id "{buyer.id}" created', 'success')
        return True

    except sqlalchemy.exc.IntegrityError:
        flash('ERROR: A buyer with this CNIC already exists!', 'danger')
        return False


def editbuyer_(buyer_id, buyer_data):

    try:
        db.session.query(Buyer).filter_by(
            id=buyer_id
        ).update({
            'name': buyer_data.name.data,
            'cnic': buyer_data.cnic.data,
            'phone': buyer_data.phone.data,
            'email': buyer_data.email.data,
            'address': buyer_data.address.data,
            'comments': buyer_data.comments.data if buyer_data.comments.data else db.null()
        })
        db.session.commit()
        flash(f'Buyer Info with id "{buyer_id}" Updated', 'success')
        return True

    except sqlalchemy.orm.exc.NoResultFound:
        flash("ERROR: A buyer with this CNIC already exists!", "danger")
        return False


def deletebuyer_(buyer):

    db.session.delete(buyer)
    db.session.commit()

    flash('Buyer Record Deleted!', 'danger')

### Commission Agent ###
def addagent_(agent):
    try:
        agent = CommissionAgent(
            name=agent['name'],
            cnic=agent['cnic'],
            phone=agent['phone'],
            email=agent['email'],
            cnic_front=agent['cnic_front'],
            cnic_back=agent['cnic_back'],
            comments=agent['comments']
        )

        db.session.add(agent)
        db.session.commit()

        flash(f'Agent with id "{agent.id}" created', 'success')
        return True

    except sqlalchemy.exc.IntegrityError:
        flash('ERROR: An Agent with this CNIC already exists!', 'danger')
        return False


def editagent_(agent_id, agent_data):

    try:
        db.session.query(CommissionAgent).filter_by(
                            id=agent_id
                            ).update({ 
                                'name'     : agent_data.name.data,
                                'cnic'     : agent_data.cnic.data,
                                'phone'    : agent_data.phone.data,
                                'email'    : agent_data.email.data,
                                'comments' : agent_data.comments.data if agent_data.comments.data else db.null()
        })

        db.session.commit()
        flash(f"Agent Info with id '{agent_id}' Updated", 'success')
        return True

    except sqlalchemy.orm.exc.NoResultFound:
        flash("ERROR: A agent with this CNIC already exists!", "danger")
        return False


def deleteagent_(agent):
    db.session.delete(agent)
    db.session.commit()

    flash('Agent Record Deleted!', 'danger')

def adddeal_(deal_data):

    plot = Plot.query.filter_by(id=deal_data['plot_id']).first()
    buyer = Buyer.query.filter_by(id=deal_data['buyer_id']).first()
    CA = CommissionAgent.query.filter_by(id=deal_data['CA_id']).first()

    if plot is None:
        flash('No Plot Selected', 'danger')
        return 'plot error'
    elif buyer is None:
        flash('No Buyer Selected', 'danger')
        return 'buyer error'

    print(
        f"------------------------\nPLOT ID: {plot}\nBUYER ID: {buyer}\nCA ID: {CA}\n------------------------")

    # Setting the plot price according to the price provided by user
    db.session.query(Plot).filter_by(id=deal_data['plot_id']).update(
        {'price': deal_data['plot_price']})
    db.session.commit()
    db.session.refresh(plot)

    # UPDATING CORESPONDING PLOT AND DEAL STATUS
    if (deal_data['first_amount_recieved'] == plot.price):
        plot.status = 'sold'
        deal_status = 'completed'
    else:
        plot.status = 'in a deal'
        deal_status = 'on going'

    db.session.add(plot)

    print(plot.status, deal_status)

    # Creating Deal and adding to Database
    deal = Deal(
        status=deal_status,
        signing_date=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        amount_per_installment=deal_data['amount_per_installment'] if deal_data['amount_per_installment'] else db.null(
        ),
        installment_frequency=deal_data['installment_frequency'] if deal_data['installment_frequency'] else db.null(
        ),
        commission_rate=deal_data['c_rate'] if deal_data['c_rate'] else db.null(
        ),
        comments=deal_data['comments'] if deal_data['comments'] else db.null(),
        buyer_id=deal_data['buyer_id'],
        plot_id=deal_data['plot_id'],
        commission_agent_id=CA.id if CA else db.null(),
    )

    db.session.add(deal)
    db.session.commit()
    db.session.refresh(deal)

    # Adding Deal Attachments to the Database
    for attachment in deal_data['attachments']:
        file = File(
            format=attachment.filename.split('.')[-1],
            data=attachment.read(),
            deal_id=deal.id,
            buyer_id=db.null()
        )
        db.session.add(file)

    # Creating corresponding transaction and adding to Database
    transaction = Transaction(
        amount=deal_data['first_amount_recieved'],
        date_time=datetime.now(),
        comments=f'Initial Transaction for Deal {deal.id}',
        deal_id=deal.id,
        expenditure_id=db.null()
    )

    db.session.add(transaction)
    db.session.commit()

    flash(f'Deal with ID {deal.id} successfully created!', 'success')
