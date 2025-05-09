import sys
import json


def get_mensualite_credit(capital, credit_info):
    t = (credit_info['taux'] / 100) / 12
    n = credit_info['années'] * 12
    mensualite_hors_assurance = capital * t / (1 - (1 + t) ** -n)
    return round(mensualite_hors_assurance + credit_info["assu_par_mois"], 2)


def charger_donnees(path):
    with open(path) as f:
        return json.load(f)


def charger_donnees_calculées(path):
    dico = charger_donnees(path)

    salaire_80 = dico['marine']['salaire_mois_net']
    has_salaire_80 = dico['marine'].get('80', False)
    salaire_100 = round((salaire_80 / 80) * 100) if has_salaire_80 else salaire_80
    nature = dico['marine']['nature_mois']
    salaire_total = salaire_100 + nature

    apport_marine = dico['marine']['apport']
    apport_franck = dico['franck']['apport']
    apport_total = apport_marine + apport_franck

    maison_ref_prix = dico['maison_ref']['prix_annonce']
    maison_ref_cout = maison_ref_prix
    maison_reelle_prix = dico['maison_reelle']['prix_maison']
    emprunt = maison_ref_cout - apport_total

    mensualite = get_mensualite_credit(emprunt, dico['credit'])
    cout_foyer_mensuel_hors_credit = dico['foyer']['cout_hors_credit']
    cout_foyer_mensuel_total = mensualite + cout_foyer_mensuel_hors_credit

    base = {
        "salaire_marine_80": salaire_80,
        "salaire_marine_100": salaire_100,
        "salaire_marine_total": salaire_total,
        "has_salaire_80": has_salaire_80,
        "nature_marine": nature,
        "apport_marine": apport_marine,
        "apport_franck": apport_franck,
        "apport_total": apport_total,
        "maison_ref_prix": maison_ref_prix,
        "maison_ref_cout": maison_ref_cout,
        "maison_reelle_prix": maison_reelle_prix,
        "emprunt": emprunt,
        "mensualite": mensualite,
        "cout_foyer_mensuel_hors_credit": cout_foyer_mensuel_hors_credit,
        "cout_foyer_mensuel_total": cout_foyer_mensuel_total,
        "contributions": []
    }

    for contrib in dico['marine']['contribs_cc']:
        contrib_mensuelle_hors_nature_marine = contrib
        contrib_mensuelle_totale_marine = contrib + nature
        contrib_mensuelle_pct_marine = round((contrib_mensuelle_totale_marine / cout_foyer_mensuel_total) * 100, 2)
        contrib_mensuelle_totale_franck = cout_foyer_mensuel_total - contrib_mensuelle_totale_marine
        contrib_mensuelle_pct_franck = round((contrib_mensuelle_totale_franck / cout_foyer_mensuel_total) * 100, 2)

        invest_marine_ref = round(apport_marine + (contrib_mensuelle_pct_marine / 100) * (maison_ref_prix - apport_total))
        invest_franck_ref = maison_ref_prix - invest_marine_ref
        invest_marine_ref_pct = round(invest_marine_ref / maison_ref_prix * 100, 2)
        invest_franck_ref_pct = round(100 - invest_marine_ref_pct, 2)

        invest_marine_reelle = invest_marine_ref
        invest_franck_reelle = maison_reelle_prix - invest_marine_reelle
        invest_marine_reelle_pct = round(invest_marine_reelle / maison_reelle_prix * 100, 2)
        invest_franck_reelle_pct = round(100 - invest_marine_reelle_pct, 2)

        base["contributions"].append({
            "contrib_mensuelle_hors_nature_marine": contrib_mensuelle_hors_nature_marine,
            "contrib_mensuelle_totale_marine": contrib_mensuelle_totale_marine,
            "contrib_mensuelle_pct_marine": contrib_mensuelle_pct_marine,
            "contrib_mensuelle_totale_franck": contrib_mensuelle_totale_franck,
            "contrib_mensuelle_pct_franck": contrib_mensuelle_pct_franck,
            "invest_marine_ref": invest_marine_ref,
            "invest_marine_ref_pct": invest_marine_ref_pct,
            "invest_franck_ref": invest_franck_ref,
            "invest_franck_ref_pct": invest_franck_ref_pct,
            "invest_marine_reelle": invest_marine_reelle,
            "invest_marine_reelle_pct": invest_marine_reelle_pct,
            "invest_franck_reelle": invest_franck_reelle,
            "invest_franck_reelle_pct": invest_franck_reelle_pct
        })

    return base


def afficher_donnees(donnees):
    if donnees["has_salaire_80"]:
        print(f"Salaire Marine 80 % / mois net : {donnees['salaire_marine_80']} €")
    print(f"Salaire Marine 100 % / mois net : {donnees['salaire_marine_100']} €")
    print(f"Salaire Marine avec avantages : {donnees['salaire_marine_total']} €")
    print(f"Apport Marine : {donnees['apport_marine']} €")
    print(f"Apport Franck : {donnees['apport_franck']} €")
    print(f"Apport Total : {donnees['apport_total']} €")
    print(f"Maison référence (annonce) : {donnees['maison_ref_prix']} €")
    print(f"Maison référence (négociée + frais) : {donnees['maison_ref_cout']} €")
    print(f"Maison réelle : {donnees['maison_reelle_prix']} €")
    print(f"Montant emprunté : {donnees['emprunt']} €")
    print(f"Mensualité crédit : {donnees['mensualite']} €")
    print(f"Foyer mensuel (hors crédit) : {donnees['cout_foyer_mensuel_hors_credit']} €")
    print(f"Foyer mensuel (total) : {donnees['cout_foyer_mensuel_total']} €")

    for c in donnees["contributions"]:
        print("*********")
        print(f"Contrib mensuelle Marine : {c['contrib_mensuelle_totale_marine']} € "
              f"({c['contrib_mensuelle_hors_nature_marine']} + {donnees['nature_marine']}) "
              f"({c['contrib_mensuelle_pct_marine']} %)")
        print(f"Contrib mensuelle Franck : {c['contrib_mensuelle_totale_franck']} € "
              f"({c['contrib_mensuelle_pct_franck']} %)")
        print("Investi après 25 ans (maison ref) :")
        print(f"  - Marine : {c['invest_marine_ref']} € ({c['invest_marine_ref_pct']} %)")
        print(f"  - Franck : {c['invest_franck_ref']} € ({c['invest_franck_ref_pct']} %)")
        print("Investi après 25 ans (maison réelle) :")
        print(f"  - Marine : {c['invest_marine_reelle']} € ({c['invest_marine_reelle_pct']} %)")
        print(f"  - Franck : {c['invest_franck_reelle']} € ({c['invest_franck_reelle_pct']} %)")


def main():
    donnees = charger_donnees_calculées(sys.argv[1])
    afficher_donnees(donnees)


if __name__ == '__main__':
    main()

