"""
Authors :
Idea By : Shivangi Mittal (@shivangimittal41)
Developer : Dhruv Kanojia (@Xonshiz)
UX : Ankit Passi (@ankitpassi141)
"""

from __future__ import print_function
import json

try:
    import requests
except:
    from botocore.vendored import requests

NEWS_API = 'YOUR_NEWSAPI_ORG_API_KEY'

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session, image_url):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Standard',
            'title': title,
            'text': output,
            'image': {
                "smallImageUrl": image_url,
                "largeImageUrl": image_url
            }
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome To Newsify"
    speech_output = "Welcome to the Newsify. " \
                    "Please speak... Latest News In, followed by the category. "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me which category's news you would like me to recite "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session, 'https://xonshiz.heliohost.org/welcome.jpg'))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying Newsify. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session, 'https://xonshiz.heliohost.org/welcome.jpg'))


def fetch_news_from_api(intent, session):
    search_category = intent['slots']['news_category']['value']
    speech_output = 'Top 5 News Headlines In {0} Category Are : '.format(search_category)

    session_attributes = {
        'news': [

        ]
    }
    session_attributes['news'] = []
    should_end_session = False
    reprompt_text = None
    # print("Checking Internet...")
    connection = requests.get(
        'https://newsapi.org/v2/top-headlines?q={0}&language=en&apiKey={1}'.format(search_category, NEWS_API))
    news_json = json.loads(connection.content.replace('\r\n', ''))
    print('Articles Count : {0}'.format(news_json['articles']))
    if news_json['articles']:
        for x in range(0, 6):
            speech_output += str(news_json['articles'][x]['title']) + '. '

            session_attributes['news'].append({
                'title': news_json['articles'][x]['title'],
                'description': news_json['articles'][x]['description'],
                'url': news_json['articles'][x]['url'],
                'image': news_json['articles'][x]['urlToImage'],
                'publishing_date': news_json['articles'][x]['publishedAt']
            })

        # print('speech_output is : {0}'.format(speech_output))
        return build_response(session_attributes, build_speechlet_response(
            intent['name'], speech_output, reprompt_text, should_end_session, str(news_json['articles'][0]['urlToImage'])))
    else:
        return build_response(session_attributes, build_speechlet_response(
            intent['name'], 'No Articles Found', reprompt_text, should_end_session,
            'https://xonshiz.heliohost.org/welcome.jpg'))


def region_based_news(intent, session):
    session_attributes = {
        'news': [

        ]
    }
    session_attributes['news'] = []
    reprompt_text = None
    should_end_session = False
    speech_output = ''
    search_country = country_name_to_code(intent['slots']['country_of_event']['value'])
    print('Search Country : {0}'.format(search_country))
    print('URL : {0}'.format(
        'https://newsapi.org/v2/top-headlines?country={0}&language=en&apiKey={1}'.format(
            search_country, NEWS_API)))

    if not search_country:
        return build_response(session_attributes, build_speechlet_response(
            intent['name'], 'You need to provide a valid country name', reprompt_text, should_end_session,
            'https://xonshiz.heliohost.org/welcome.jpg'))

    # speech_output = 'Selected Country Is {0}'.format(search_country)

    """The 2-letter ISO 3166-1 code of the country you want to get headlines for.
    Read More @ https://newsapi.org/docs/endpoints/top-headlines
    """
    connection = requests.get(
        'https://newsapi.org/v2/top-headlines?country={0}&language=en&apiKey={1}'.format(
            search_country, NEWS_API))
    news_json = json.loads(connection.content.replace('\r\n', ''))
    print('Articles Count : {0}'.format(news_json['articles']))
    if news_json['articles']:
        for x in range(0, 6):
            speech_output += str(news_json['articles'][x]['title']) + '. '
            session_attributes['news'].append({
                'title': news_json['articles'][x]['title'],
                'description': news_json['articles'][x]['description'],
                'url': news_json['articles'][x]['url'],
                'image': news_json['articles'][x]['urlToImage'],
                'publishing_date': news_json['articles'][x]['publishedAt']
            })

        print('speech_output is : {0}'.format(speech_output))
        return build_response(session_attributes, build_speechlet_response(
            intent['name'], speech_output, reprompt_text, should_end_session, str(news_json['articles'][0]['urlToImage'])))
    else:
        return build_response(session_attributes, build_speechlet_response(
            intent['name'], 'No Articles Found', reprompt_text, should_end_session,
            'https://xonshiz.heliohost.org/welcome.jpg'))


def news_information(intent, session):
    session_attributes = {}
    reprompt_text = None
    should_end_session = True

    news_index = int(single_news_index_maker(intent['slots']['news_index']['value']))
    if news_index == 0:
        news_index = 0
    else:
        news_index = news_index - 1
    # session_attributes_fetched = json.loads(json.dumps(session['attributes']))
    if not session.get('attributes'):
        return build_response(session_attributes, build_speechlet_response(
            intent['name'], 'You have not specified the news categories or country.', reprompt_text, should_end_session,
            'https://xonshiz.heliohost.org/welcome.jpg'))
    news_title = session['attributes']['news'][news_index]['title']
    news_description = session['attributes']['news'][news_index]['description']
    news_url = session['attributes']['news'][news_index]['url']
    news_image = session['attributes']['news'][news_index]['image']
    news_publishing_date = session['attributes']['news'][news_index]['publishing_date']
    speech_output = news_description
    session_attributes.clear()
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session, news_image))


# --------------- Events ------------------


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == "NewsCategory":
        return fetch_news_from_api(intent, session)
    elif intent_name == "RegionBasedNews":
        return region_based_news(intent, session)
    elif intent_name == "SingleNewsInformation":
        return news_information(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends json_data to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


# --------------- Main handler ------------------


def country_name_to_code(country_name):
    """https://stackoverflow.com/a/16263580/2408212

    The 2-letter ISO 3166-1 code of the country you want to get headlines for.
    Read More @ https://newsapi.org/docs/endpoints/top-headlines
    :param country_name:
    :return:
    """
    code_dict = {'Afghanistan': 'AF',
                 'Albania': 'AL',
                 'America': 'US',
                 'Algeria': 'DZ',
                 'American Samoa': 'AS',
                 'Andorra': 'AD',
                 'Angola': 'AO',
                 'Anguilla': 'AI',
                 'Antarctica': 'AQ',
                 'Antigua and Barbuda': 'AG',
                 'Argentina': 'AR',
                 'Armenia': 'AM',
                 'Aruba': 'AW',
                 'Australia': 'AU',
                 'Austria': 'AT',
                 'Azerbaijan': 'AZ',
                 'Bahamas': 'BS',
                 'Bahrain': 'BH',
                 'Bangladesh': 'BD',
                 'Barbados': 'BB',
                 'Belarus': 'BY',
                 'Belgium': 'BE',
                 'Belize': 'BZ',
                 'Benin': 'BJ',
                 'Bermuda': 'BM',
                 'Bhutan': 'BT',
                 'Bolivia, Plurinational State of': 'BO',
                 'Bonaire, Sint Eustatius and Saba': 'BQ',
                 'Bosnia and Herzegovina': 'BA',
                 'Botswana': 'BW',
                 'Bouvet Island': 'BV',
                 'Brazil': 'BR',
                 'British Indian Ocean Territory': 'IO',
                 'Brunei Darussalam': 'BN',
                 'Bulgaria': 'BG',
                 'Burkina Faso': 'BF',
                 'Burundi': 'BI',
                 'Cambodia': 'KH',
                 'Cameroon': 'CM',
                 'Canada': 'CA',
                 'Cape Verde': 'CV',
                 'Cayman Islands': 'KY',
                 'Central African Republic': 'CF',
                 'Chad': 'TD',
                 'Chile': 'CL',
                 'China': 'CN',
                 'Christmas Island': 'CX',
                 'Cocos (Keeling) Islands': 'CC',
                 'Colombia': 'CO',
                 'Comoros': 'KM',
                 'Congo': 'CG',
                 'Congo, the Democratic Republic of the': 'CD',
                 'Cook Islands': 'CK',
                 'Costa Rica': 'CR',
                 'Country name': 'Code',
                 'Croatia': 'HR',
                 'Cuba': 'CU',
                 'Curacao': 'CW',
                 'Cyprus': 'CY',
                 'Czech Republic': 'CZ',
                 "Cote d'Ivoire": 'CI',
                 'Denmark': 'DK',
                 'Djibouti': 'DJ',
                 'Dominica': 'DM',
                 'Dominican Republic': 'DO',
                 'Ecuador': 'EC',
                 'Egypt': 'EG',
                 'El Salvador': 'SV',
                 'Equatorial Guinea': 'GQ',
                 'Eritrea': 'ER',
                 'Estonia': 'EE',
                 'Ethiopia': 'ET',
                 'Falkland Islands (Malvinas)': 'FK',
                 'Faroe Islands': 'FO',
                 'Fiji': 'FJ',
                 'Finland': 'FI',
                 'France': 'FR',
                 'French Guiana': 'GF',
                 'French Polynesia': 'PF',
                 'French Southern Territories': 'TF',
                 'Gabon': 'GA',
                 'Gambia': 'GM',
                 'Georgia': 'GE',
                 'Germany': 'DE',
                 'Ghana': 'GH',
                 'Gibraltar': 'GI',
                 'Greece': 'GR',
                 'Greenland': 'GL',
                 'Grenada': 'GD',
                 'Guadeloupe': 'GP',
                 'Guam': 'GU',
                 'Guatemala': 'GT',
                 'Guernsey': 'GG',
                 'Guinea': 'GN',
                 'Guinea-Bissau': 'GW',
                 'Guyana': 'GY',
                 'Haiti': 'HT',
                 'Heard Island and McDonald Islands': 'HM',
                 'Holy See (Vatican City State)': 'VA',
                 'Honduras': 'HN',
                 'Hong Kong': 'HK',
                 'Hungary': 'HU',
                 'ISO 3166-2:GB': '(.uk)',
                 'Iceland': 'IS',
                 'India': 'IN',
                 'Indonesia': 'ID',
                 'Iran, Islamic Republic of': 'IR',
                 'Iraq': 'IQ',
                 'Ireland': 'IE',
                 'Isle of Man': 'IM',
                 'Israel': 'IL',
                 'Italy': 'IT',
                 'Jamaica': 'JM',
                 'Japan': 'JP',
                 'Jersey': 'JE',
                 'Jordan': 'JO',
                 'Kazakhstan': 'KZ',
                 'Kenya': 'KE',
                 'Kiribati': 'KI',
                 "Korea, Democratic People's Republic of": 'KP',
                 'Korea, Republic of': 'KR',
                 'Kuwait': 'KW',
                 'Kyrgyzstan': 'KG',
                 "Lao People's Democratic Republic": 'LA',
                 'Latvia': 'LV',
                 'Lebanon': 'LB',
                 'Lesotho': 'LS',
                 'Liberia': 'LR',
                 'Libya': 'LY',
                 'Liechtenstein': 'LI',
                 'Lithuania': 'LT',
                 'Luxembourg': 'LU',
                 'Macao': 'MO',
                 'Macedonia, the former Yugoslav Republic of': 'MK',
                 'Madagascar': 'MG',
                 'Malawi': 'MW',
                 'Malaysia': 'MY',
                 'Maldives': 'MV',
                 'Mali': 'ML',
                 'Malta': 'MT',
                 'Marshall Islands': 'MH',
                 'Martinique': 'MQ',
                 'Mauritania': 'MR',
                 'Mauritius': 'MU',
                 'Mayotte': 'YT',
                 'Mexico': 'MX',
                 'Micronesia, Federated States of': 'FM',
                 'Moldova, Republic of': 'MD',
                 'Monaco': 'MC',
                 'Mongolia': 'MN',
                 'Montenegro': 'ME',
                 'Montserrat': 'MS',
                 'Morocco': 'MA',
                 'Mozambique': 'MZ',
                 'Myanmar': 'MM',
                 'Namibia': 'NA',
                 'Nauru': 'NR',
                 'Nepal': 'NP',
                 'Netherlands': 'NL',
                 'New Caledonia': 'NC',
                 'New Zealand': 'NZ',
                 'Nicaragua': 'NI',
                 'Niger': 'NE',
                 'Nigeria': 'NG',
                 'Niue': 'NU',
                 'Norfolk Island': 'NF',
                 'Northern Mariana Islands': 'MP',
                 'Norway': 'NO',
                 'Oman': 'OM',
                 'Pakistan': 'PK',
                 'Palau': 'PW',
                 'Palestine, State of': 'PS',
                 'Panama': 'PA',
                 'Papua New Guinea': 'PG',
                 'Paraguay': 'PY',
                 'Peru': 'PE',
                 'Philippines': 'PH',
                 'Pitcairn': 'PN',
                 'Poland': 'PL',
                 'Portugal': 'PT',
                 'Puerto Rico': 'PR',
                 'Qatar': 'QA',
                 'Romania': 'RO',
                 'Russian Federation': 'RU',
                 'Rwanda': 'RW',
                 'Reunion': 'RE',
                 'Saint Barthelemy': 'BL',
                 'Saint Helena, Ascension and Tristan da Cunha': 'SH',
                 'Saint Kitts and Nevis': 'KN',
                 'Saint Lucia': 'LC',
                 'Saint Martin (French part)': 'MF',
                 'Saint Pierre and Miquelon': 'PM',
                 'Saint Vincent and the Grenadines': 'VC',
                 'Samoa': 'WS',
                 'San Marino': 'SM',
                 'Sao Tome and Principe': 'ST',
                 'Saudi Arabia': 'SA',
                 'Senegal': 'SN',
                 'Serbia': 'RS',
                 'Seychelles': 'SC',
                 'Sierra Leone': 'SL',
                 'Singapore': 'SG',
                 'Sint Maarten (Dutch part)': 'SX',
                 'Slovakia': 'SK',
                 'Slovenia': 'SI',
                 'Solomon Islands': 'SB',
                 'Somalia': 'SO',
                 'South Africa': 'ZA',
                 'South Georgia and the South Sandwich Islands': 'GS',
                 'South Sudan': 'SS',
                 'Spain': 'ES',
                 'Sri Lanka': 'LK',
                 'Sudan': 'SD',
                 'Suriname': 'SR',
                 'Svalbard and Jan Mayen': 'SJ',
                 'Swaziland': 'SZ',
                 'Sweden': 'SE',
                 'Switzerland': 'CH',
                 'Syrian Arab Republic': 'SY',
                 'Taiwan, Province of China': 'TW',
                 'Tajikistan': 'TJ',
                 'Tanzania, United Republic of': 'TZ',
                 'Thailand': 'TH',
                 'Timor-Leste': 'TL',
                 'Togo': 'TG',
                 'Tokelau': 'TK',
                 'Tonga': 'TO',
                 'Trinidad and Tobago': 'TT',
                 'Tunisia': 'TN',
                 'Turkey': 'TR',
                 'Turkmenistan': 'TM',
                 'Turks and Caicos Islands': 'TC',
                 'Tuvalu': 'TV',
                 'Uganda': 'UG',
                 'Ukraine': 'UA',
                 'United Arab Emirates': 'AE',
                 'United Kingdom': 'GB',
                 'United States': 'US',
                 'United States Minor Outlying Islands': 'UM',
                 'Uruguay': 'UY',
                 'Uzbekistan': 'UZ',
                 'Vanuatu': 'VU',
                 'Venezuela, Bolivarian Republic of': 'VE',
                 'Viet Nam': 'VN',
                 'Virgin Islands, British': 'VG',
                 'Virgin Islands, U.S.': 'VI',
                 'Wallis and Futuna': 'WF',
                 'Western Sahara': 'EH',
                 'Yemen': 'YE',
                 'Zambia': 'ZM',
                 'Zimbabwe': 'ZW',
                 'Aland Islands': 'AX'}
    if not country_name:
        country_name = 'United States'
    return str(code_dict.get(country_name, "us")).lower().strip()


def single_news_index_maker(index_value):
    values = {
        'first': 1,
        'second': 2,
        'third': 3,
        'fourth': 4,
        'fifth': 5,
        '1st': 1,
        '2nd': 2,
        '3rd': 3,
        '4th': 4,
        '5th': 5,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
    }
    if not index_value:
        index_value = 0
    return int(values.get(index_value, 0))
