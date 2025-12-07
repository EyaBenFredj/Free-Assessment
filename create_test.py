import sqlite3
import pandas as pd

print('Creating test database...')
conn = sqlite3.connect('data/db.sqlite')

sample_data = {
    'contact_id': [1, 2, 3, 4, 5],
    'commentaire': [
        'Service excellent, très satisfait du support technique',
        'Fibre souvent en panne, débit lent',
        'Prix trop élevé pour la qualité',
        'Conseiller très professionnel et à l\'écoute',
        'Installation retardée de 3 jours, très déçu'
    ],
    'csat': [5, 2, 3, 5, 1],
    'offer_label': [
        '241 FreeBox Pop | 39.59€',
        '091 FreeBox Révolution Light | 29.99€',
        '281 Série Spéciale Freebox Pop',
        '311 FreeBox Ultra avec Player TV Free',
        '241 FreeBox Pop | 39.59€'
    ],
    'date_contact': ['2025-10-19'] * 5
}

df = pd.DataFrame(sample_data)
df.to_sql('csat_extract', conn, if_exists='replace', index=False)
conn.close()
print('✅ Test database created at data/db.sqlite')
