import json
import warnings

from elasticsearch import Elasticsearch

warnings.simplefilter("ignore")


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Connection succeed!')
    else:
        print('Connection failed!')
    return _es


es = connect_elasticsearch()


def text_processing(text):
    if text is not None:
        out_text = text.replace('\u200d', '')
    else:
        out_text = text
    return out_text


def result_text_processing(result):
    filtered_result = []
    for i in result:
        if 'tags' not in i['_source']:
            if i['_source']['name'] != 'name' and len(i['_source']['reign_start'].split(' ')) > 1 and len(
                    i['_source']['reign_end'].split(' ')) > 1:
                final_dict = {}
                final_dict['name'] = text_processing(i['_source']['name'])
                final_dict['clan'] = text_processing(i['_source']['clan'])
                final_dict['kingdom'] = text_processing(i['_source']['kingdom'])
                final_dict['reign_start'] = text_processing(i['_source']['reign_start'])
                final_dict['reign_end'] = text_processing(i['_source']['reign_end'])
                final_dict['predecessor_relation'] = text_processing(i['_source']['predecessor_relation'])
                final_dict['reign_details'] = text_processing(i['_source']['reign_details'])
                filtered_result.append(final_dict)
    return filtered_result


def query_search(index_name, search_obj):
    res = es.search(index=index_name, body=search_obj)
    if len(result_text_processing(res['hits']['hits'])) > 0:
        for i in result_text_processing(res['hits']['hits']):
            print(i)
    else:
        print('No match found!')


def sorted_query_search(index_name, search_obj, order):
    res = es.search(index=index_name, body=search_obj)
    # print(res)
    bc_list = []
    ad_list = []
    length_list = []
    if len(result_text_processing(res['hits']['hits'])) > 0:
        for i in result_text_processing(res['hits']['hits']):
            # if len(i['reign_start'].split(' ')) > 1 and len(i['reign_end'].split(' ')) > 1:
            if i['reign_start'].split(' ')[1] == 'BC':
                bc_list.append(i)
            if i['reign_start'].split(' ')[1] == 'AD':
                ad_list.append(i)
            if (i['reign_start'].split(' ')[1] == 'BC' and i['reign_end'].split(' ')[1] == 'BC') or (i['reign_start'].split(' ')[1] == 'AD' and i['reign_end'].split(' ')[1] == 'AD'):
                i['reign_length'] = abs(int(i['reign_start'].split(' ')[0]) - int(i['reign_end'].split(' ')[0]))
                if i['reign_length'] < 100:
                    length_list.append(i)
            if i['reign_start'].split(' ')[1] == 'BC' and i['reign_end'].split(' ')[1] == 'AD':
                i['reign_length'] = abs(int(i['reign_start'].split(' ')[0]) + int(i['reign_end'].split(' ')[0]))
                if i['reign_length'] < 100:
                    length_list.append(i)
        if order == 'oldest':
            for k in sorted(bc_list, key=lambda d: int(d['reign_start'].split(' ')[0]), reverse=True):
                print(k)
            for k in sorted(ad_list, key=lambda d: int(d['reign_start'].split(' ')[0])):
                print(k)
        if order == 'recent':
            for k in sorted(ad_list, key=lambda d: int(d['reign_start'].split(' ')[0]), reverse=True):
                print(k)
            for k in sorted(bc_list, key=lambda d: int(d['reign_start'].split(' ')[0])):
                print(k)
        if order == 'longest':
            for k in sorted(length_list, key=lambda d: d['reign_length'], reverse=True):
                print(k)
        if order == 'shortest':
            for k in sorted(length_list, key=lambda d: d['reign_length']):
                print(k)
    else:
        print('No match found!')


def range_search(index_name, search_obj, range_type, start_year, end_year):
    res = es.search(index=index_name, body=search_obj)
    if range_type == 'AA':  # range in AD timeline
        result_list = sorted(result_text_processing(res['hits']['hits']),
                             key=lambda d: int(d['reign_start'].split(' ')[0]))
        count = 0
        for i in result_list:
            if (start_year <= int(i['reign_start'].split(' ')[0]) <= end_year) or (
                    start_year <= int(i['reign_end'].split(' ')[0]) <= end_year):
                print(i)
                count += 1
        if count == 0:
            print('No match found!')

    if range_type == 'BB':  # range in BC timeline
        result_list = sorted(result_text_processing(res['hits']['hits']),
                             key=lambda d: int(d['reign_start'].split(' ')[0]), reverse=True)
        count = 0
        for i in result_list:
            if (end_year <= int(i['reign_start'].split(' ')[0]) <= start_year) or (
                    end_year <= int(i['reign_end'].split(' ')[0]) <= start_year):
                print(i)
                count += 1
        if count == 0:
            print('No match found!')

    if range_type == 'BA':  # range from BC timeline to AD timeline
        result_list = sorted(result_text_processing(res['hits']['hits']),
                             key=lambda d: int(d['reign_start'].split(' ')[0]), reverse=True)
        count = 0
        for i in result_list:
            if int(i['reign_start'].split(' ')[0]) <= start_year and int(i['reign_end'].split(' ')[0]) <= end_year:
                print(i)
                count += 1
        if count == 0:
            print('No match found!')


def search_all(order):
    print('Sri Lankan kings')
    if es is not None:
        search_object = {"size": 200, 'query': {'match_all': {}}}
        sorted_query_search('kings', json.dumps(search_object), order)


def search_by_name(name):
    print('Search result for name:', name)
    if es is not None:
        search_object = {"size": 20, 'query': {'wildcard': {'name': str(name)}}}
        query_search('kings', json.dumps(search_object))


def search_by_clan(clan_name, order):
    print('Search result for clan:', clan_name)
    if es is not None:
        search_object = {"size": 100, 'query': {'match': {'clan': str(clan_name)}}}
        sorted_query_search('kings', json.dumps(search_object), order)


def search_by_kingdom(kingdom_name, order):
    print('Search result for kingdom:', kingdom_name)
    if es is not None:
        search_object = {"size": 100, 'query': {'match': {'kingdom': str(kingdom_name)}}}
        sorted_query_search('kings', json.dumps(search_object), order)


def search_by_relation(relationship):
    print('Search result for predecessor_relation:', relationship)
    if es is not None:
        search_object = {"size": 20, 'query': {'match': {'predecessor_relation': str(relationship)}}}
        query_search('kings', json.dumps(search_object))


def search_by_details(detail):
    print('Search result for reign_details:', detail)
    if es is not None:
        search_object = {"size": 20, 'query': {'match': {'reign_details': str(detail)}}}
        query_search('kings', json.dumps(search_object))


# search fulltext with boosting for name, clan, kingdom fields
def search_by_fulltext(text):
    print('Search results for text:', text)
    if es is not None:
        search_object = {"size": 20, 'query': {'multi_match': {'query': str(text),
                                                               'type': "most_fields",
                                                               'fields': ["name^3", "clan^3", "kingdom^3",
                                                                          "reign_start",
                                                                          "reign_end",
                                                                          "predecessor_relation^2", "reign_details"]}}}
        query_search('kings', json.dumps(search_object))


def multi_field_search(name, clan, kingdom, relationship):
    print('Search results for name:', name, ', clan:', clan, ', kingdom:', kingdom, ', predecessor_relation:',
          relationship)
    if es is not None:
        search_object = {
            "size": 100,
            "query": {
                "bool": {
                    "must": []
                }
            }
        }
        if name is not None and len(name) > 0:
            search_object['query']['bool']['must'].append({
                "match": {
                    "name": str(name)
                }
            })
        if clan is not None and len(clan) > 0:
            search_object['query']['bool']['must'].append({
                "match": {
                    "clan": str(clan)
                }
            })
        if kingdom is not None and len(kingdom) > 0:
            search_object['query']['bool']['must'].append({
                "match": {
                    "kingdom": str(kingdom)
                }
            })
        if relationship is not None and len(relationship) > 0:
            search_object['query']['bool']['must'].append({
                "match": {
                    "predecessor_relation": str(relationship)
                }
            })
        query_search('kings', json.dumps(search_object))


def search_by_range(start, end):
    print('Kings who reigned the Sri Lanka in', start, '-', end, 'time period.')
    if es is not None:
        start_year, start_timeline = start.split(' ')
        end_year, end_timeline = end.split(' ')
        search_object = {
            "size": 200,
            "query": {
                "bool": {
                    "filter": []
                }
            }
        }
        if start_timeline == 'AD' and end_timeline == 'AD':
            search_object['query']['bool']['filter'].append({
                "match": {
                    "reign_start": 'AD'
                }
            })
            search_object['query']['bool']['filter'].append({
                "match": {
                    "reign_end": 'AD'
                }
            })
            range_search('kings', json.dumps(search_object), 'AA', int(start_year), int(end_year))
        elif start_timeline == 'BC' and end_timeline == 'BC':
            search_object['query']['bool']['filter'].append({
                "match": {
                    "reign_start": 'BC'
                }
            })
            search_object['query']['bool']['filter'].append({
                "match": {
                    "reign_end": 'BC'
                }
            })
            range_search('kings', json.dumps(search_object), 'BB', int(start_year), int(end_year))
        elif start_timeline == 'BC' and end_timeline == 'AD':
            search_object_bb = {
                "size": 200,
                "query": {
                    "bool": {
                        "filter": []
                    }
                }
            }
            search_object_aa = {
                "size": 200,
                "query": {
                    "bool": {
                        "filter": []
                    }
                }
            }
            search_object_ba = {
                "size": 200,
                "query": {
                    "bool": {
                        "filter": []
                    }
                }
            }
            search_object_bb['query']['bool']['filter'].append({
                "match": {
                    "reign_start": 'BC'
                }
            })
            search_object_bb['query']['bool']['filter'].append({
                "match": {
                    "reign_end": 'BC'
                }
            })
            search_object_aa['query']['bool']['filter'].append({
                "match": {
                    "reign_start": 'AD'
                }
            })
            search_object_aa['query']['bool']['filter'].append({
                "match": {
                    "reign_end": 'AD'
                }
            })
            search_object_ba['query']['bool']['filter'].append({
                "match": {
                    "reign_start": 'BC'
                }
            })
            search_object_ba['query']['bool']['filter'].append({
                "match": {
                    "reign_end": 'AD'
                }
            })
            range_search('kings', json.dumps(search_object_bb), 'BB', int(start_year), 0)
            range_search('kings', json.dumps(search_object_ba), 'BA', int(start_year), int(end_year))
            range_search('kings', json.dumps(search_object_aa), 'AA', 0, int(end_year))
        else:
            print('Invalid year range!')


if __name__ == '__main__':
    while True:
        print('Enter the associate number to select the search option \n')
        print(
            'search_by_name: 1 \nsearch_by_clan: 2 \nsearch_by_kingdom: 3 \nsearch_by_predecessor_relation: 4 \n'
            'search_by_reign_details: 5 \nsearch_by_fulltext: 6 \nmultiple_field_search: 7 \n'
            'range_search_by_reign_years: 8 \nRetrieve all: 9')
        option = input('Search option:').strip()
        if option == '1':
            print('Insert your search text')
            name = input('Name:').strip()
            search_by_name(name)

        elif option == '2':
            print('Insert your search text')
            clan = input('Clan:').strip()
            print('Order preference \nOldest - 1\nRecent - 2 \nLongest - 3 \nShortest - 4')
            order = input('Order:').strip()
            if order == '1':
                search_by_clan(clan, 'oldest')
            elif order == '2':
                search_by_clan(clan, 'recent')
            elif order == '3':
                search_by_clan(clan, 'longest')
            elif order == '4':
                search_by_clan(clan, 'shortest')
            else:
                print('Invalid preference!')

        elif option == '3':
            print('Insert your search text')
            kingdom = input('Kingdom:').strip()
            print('Order preference \nOldest - 1\nRecent - 2 \nLongest - 3 \nShortest - 4')
            order = input('Order:').strip()
            if order == '1':
                search_by_kingdom(kingdom, 'oldest')
            elif order == '2':
                search_by_kingdom(kingdom, 'recent')
            elif order == '3':
                search_by_kingdom(kingdom, 'longest')
            elif order == '4':
                search_by_kingdom(kingdom, 'shortest')
            else:
                print('Invalid preference!')

        elif option == '4':
            print('Insert your search text')
            relation = input('Predecessor relation:').strip()
            search_by_relation(relation)

        elif option == '5':
            print('Insert your search text')
            details = input('Reign details:').strip()
            search_by_details(details)

        elif option == '6':
            print('Insert your search text')
            text = input('Input text:').strip()
            search_by_fulltext(text)

        elif option == '7':
            print('Insert your search texts to corresponding fields')
            name = input('Name:').strip()
            clan = input('Clan:').strip()
            kingdom = input('Kingdom:').strip()
            relationship = input('Predecessor relation:').strip()
            multi_field_search(name, clan, kingdom, relationship)

        elif option == '8':
            print('Insert the year range \n[example - Start year: 123 AD/BC, End year: 123 AD/BC]')
            start_year = input('Start year:').strip()
            end_year = input('End year:').strip()
            if len(start_year.split()) < 2 and len(end_year.split()) < 2:
                print('Inavlid input!')
            else:
                search_by_range(start_year, end_year)

        elif option == '9':
            print('Order preference \nOldest - 1\nRecent - 2 \nLongest - 3 \nShortest - 4')
            order = input('Order:').strip()
            if order == '1':
                search_all('oldest')
            elif order == '2':
                search_all('recent')
            elif order == '3':
                search_all('longest')
            elif order == '4':
                search_all('shortest')
            else:
                print('Invalid preference!')
        else:
            print('Invalid input!')

        more = input("Search again? [y/n]:").strip().lower()
        if more == 'n':
            break
