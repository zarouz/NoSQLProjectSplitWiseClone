def calculate_balances(expenses, members, settlements=None):
    """
    Calculate balances for all members based on expenses and settlements
    
    Args:
        expenses: List of expense dicts with amount, paidById, and participants
        members: List of member dicts with id
        settlements: List of settlement dicts (optional)
    
    Returns:
        dict: userId -> balance mapping
    """
    if settlements is None:
        settlements = []
    
    balances = {}
    for member in members:
        balances[member['id']] = 0.0
    
    # Step 1: Calculate initial balances based on expenses
    for expense in expenses:
        payer_id = expense.get('paidById')
        amount = float(expense.get('amount', 0))
        participants = expense.get('participants', [])
        num_participants = len(participants)
        
        if num_participants == 0:
            continue
        
        # Credit the person who paid the full amount
        if payer_id in balances:
            balances[payer_id] += amount
        
        # Debit each participant for their share
        share = amount / num_participants
        for participant in participants:
            participant_id = participant['id']
            if participant_id in balances:
                balances[participant_id] -= share
    
    # Step 2: Apply all settlement transactions to the balances
    for settlement in settlements:
        from_user_id = settlement.get('fromUserId')
        to_user_id = settlement.get('toUserId')
        amount = float(settlement.get('amount', 0))
        
        # The person who paid (the debtor) moves closer to zero (balance increases)
        if from_user_id in balances:
            balances[from_user_id] += amount
        
        # The person who received money (the creditor) moves closer to zero (balance decreases)
        if to_user_id in balances:
            balances[to_user_id] -= amount
    
    return balances


def settle_debts(balances):
    """
    Generate simplified payment suggestions to settle all debts
    
    Args:
        balances: dict of userId -> balance
    
    Returns:
        list: Array of payment dicts with {from, to, amount}
    """
    # Convert to list and filter out trivial amounts
    sorted_balances = [
        {'userId': user_id, 'balance': balance}
        for user_id, balance in balances.items()
        if abs(balance) > 0.01
    ]
    
    # Separate debtors (negative) and creditors (positive)
    debtors = sorted([b for b in sorted_balances if b['balance'] < 0], 
                     key=lambda x: x['balance'])
    creditors = sorted([b for b in sorted_balances if b['balance'] > 0], 
                       key=lambda x: x['balance'], reverse=True)
    
    payments = []
    debtor_idx = 0
    creditor_idx = 0
    
    while debtor_idx < len(debtors) and creditor_idx < len(creditors):
        debtor = debtors[debtor_idx]
        creditor = creditors[creditor_idx]
        
        amount_to_settle = min(-debtor['balance'], creditor['balance'])
        
        payments.append({
            'from': debtor['userId'],
            'to': creditor['userId'],
            'amount': amount_to_settle
        })
        
        debtor['balance'] += amount_to_settle
        creditor['balance'] -= amount_to_settle
        
        if abs(debtor['balance']) < 0.01:
            debtor_idx += 1
        if abs(creditor['balance']) < 0.01:
            creditor_idx += 1
    
    return payments