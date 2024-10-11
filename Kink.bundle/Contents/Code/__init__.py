#!/usr/bin/python
# -*- coding: utf-8 -*-
# Kink.com

import re
import subprocess

# URLS

EXC_BASEURL = 'https://www.kink.com/'
EXC_SEARCH_MOVIES = EXC_BASEURL + 'search?q=%s'
EXC_MOVIE_INFO = EXC_BASEURL + 'shoot/%s'
EXC_MODEL_INFO = EXC_BASEURL + 'model/%s'
EXC_RATING_API = EXC_BASEURL + 'api/ratings/%s' 

# Bash command to bypass the Plex Python downloading methods - Kink.com uses Cloudflare and it will block any invocations from the older Python 2.7 web scraping methods
BASH_COMMAND = "wget -qO- --header='Cookie: ct=2' --header='User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', --header='Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', --header='Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3', --header='Accept-Encoding: none', --header='Accept-Language: en-US,en;q=0.8', --header='Connection: keep-alive' %s"

# XPath strings to fetch movie metadata - first place to look in case of issues once Kink changes frontend
SITENAME_XPATH = '/html/body/div[2]/div/div[1]/div[2]/div/div[3]/span[1]/a/text()'
TAGS_XPATH = '/html/body/div[2]/div/div[1]/div[4]/span[2]/a'
TITLE_XPATH = '/html/body/div[2]/div/div[1]/div[2]/div/div[4]/h1/text()'
RELEASEDATE_XPATH = '/html/body/div[2]/div/div[1]/div[2]/div/div[3]/span[2]'
POSTER_XPATH = '//video/@poster'
MOVIEART_XPATH = '//img[contains(@class, "gallery-img")]'
SUMMARY_XPATH = '//div[contains(@class, "shoot-detail-description")]/span/p'
DIRECTOR_XPATH = '//span[contains(@class, "director-name")]/a'
STARRING_XPATH = '//html/body/div[2]/div/div[1]/div[2]/div/div[4]/span/a'


def HttpReq(url):
    Log(' Requesting: %s' % url)

    try:
        bashCommand = BASH_COMMAND % url
        output = subprocess.check_output(bashCommand, shell=True,
                stderr=subprocess.STDOUT)
        return output
    except subprocess.CalledProcessError, e:
        Log('Exception ' + e.output)


class KinkAgent(Agent.Movies):

    name = 'Kink.com'
    languages = [Locale.Language.English]
    accepts_from = ['com.plexapp.agents.localmedia']
    primary_provider = True

    def search(
        self,
        results,
        media,
        lang,
        ):

        title = media.name
        if media.primary_metadata is not None:
            title = media.primary_metadata.title

        episodeMatch = re.match(r'(?:[A-Za-z]{2,4}[- ])?(\d{3,})',
                                title)

    # if file starts with episode id, just go directly to that episode
        if episodeMatch is not None:
            Log('Match result for search: ' + media.name + ' is '
            + episodeMatch.group(1))
            episodeId = episodeMatch.group(1)
            results.Append(MetadataSearchResult(id=episodeId,
                           name=title, score=90, lang=lang))
        else:
            Log('No matches for : ' + media.name + ', falling back to more aggressive regex')
            episodeMatch = re.findall(r'(\d{3,})',
                                title)
            episodeId = episodeMatch[0]
            results.Append(MetadataSearchResult(id=episodeId,
                           name=title, score=90, lang=lang))

        results.Sort('score', descending=True)

    def update(
        self,
        metadata,
        media,
        lang,
        ):

        Log('Attempting to match: ' + metadata.id + ' at '
            + EXC_MOVIE_INFO % metadata.id)
        html = HTML.ElementFromString(HttpReq(EXC_MOVIE_INFO % metadata.id))

    # use site name as movie studio
    # add site name to genres

        metadata.genres.clear()
        try:
            sitename = \
                html.xpath(SITENAME_XPATH)[0]
            Log('Sitename ' + sitename)
            metadata.studio = sitename.strip()
        except Exception, e:
            Log('Sitename exception' + str(e))

    # add channels to genres
    # add other tags to collections

        metadata.collections.clear()
        try:
            tags = \
                html.xpath(TAGS_XPATH)
            for tag in tags:
                Log('Tag ' + tag.text_content())
                metadata.collections.add(tag.text_content().strip().replace(',', ''))
        except Exception, e:
            Log('Tag Collections exception' + str(e))

    # set movie title to shoot title

        metadata.title = \
            html.xpath(TITLE_XPATH)[0] + ' (' + metadata.id + ')'
        Log('Title ' + metadata.title)

    # set content rating to XXX

        metadata.content_rating = 'XXX'

    # set episode ID as tagline for easy visibility

        metadata.tagline = metadata.studio + ' \xe2\x80\x93 ' \
            + metadata.id

    # set movie release date to shoot release date

        try:
            release_date = \
                html.xpath(RELEASEDATE_XPATH)[0].text_content().replace('Date: ', '')
            metadata.originally_available_at = \
                Datetime.ParseDate(release_date).date()
            metadata.year = metadata.originally_available_at.year
            Log('Date ' + str(metadata.originally_available_at))
            Log('Year ' + str(metadata.originally_available_at.year))
        except Exception, e:
            Log('Date exception' + str(e))

    # set poster to the image that kink.com chose as preview

        try:
            thumbpUrl = html.xpath(POSTER_XPATH)[0]
            thumbp = HTTP.Request(thumbpUrl)
            Log('Poster URL ' + thumbpUrl)
            metadata.posters[thumbpUrl] = Proxy.Media(thumbp)
        except Exception, e:
            Log('Poster exception' + str(e))

    # fill movie art with all images, so they can be used as backdrops

        try:
            imgs = html.xpath(MOVIEART_XPATH)
            for img in imgs:
            	Log('Movie Art URL ' + img.get('data-image-file'))
                thumbUrl = re.sub(r'/h/[0-9]{3,3}/', r'/h/830/',
                                  img.get('data-image-file'))
                thumb = HTTP.Request(thumbUrl)
                metadata.art[thumbUrl] = Proxy.Media(thumb)
        except Exception, e:
            Log('Thumb exception' + str(e))

    # summary

        try:
            metadata.summary = ''
            summary = \
                html.xpath(SUMMARY_XPATH)[0]
            metadata.summary = \
                summary.text_content().strip().replace('<br>', '\n')
            metadata.summary.strip()
            Log('Summary ' + metadata.summary)
        except Exception, e:
            Log('Summary error ' + str(e))

    # director

        try:
            metadata.directors.clear()
            director_name = \
                html.xpath(DIRECTOR_XPATH)[0]
            Log('Director name ' + director_name.text_content())
            try:
                director = metadata.directors.new()
                director.name = director_name.text_content()
            except:
                try:
                    metadata.directors.add(director_name.text_content())
                except:
                    pass
        except Exception, e:
            Log('Director error ' + str(e))

    # starring

        try:
            starring = \
                html.xpath(STARRING_XPATH)
            metadata.roles.clear()
            for member in starring:
            	Log('Starring ' + member.text_content().strip())
                role = metadata.roles.new()
                lename = member.text_content().strip()
                try:
                    role.name = lename.replace(',', '')
                except:
                    try:
                        role.actor = lename.replace(',', '')
                    except:
                        pass
        except:
            pass

    # rating

        try:
            rating_json = HttpReq(EXC_RATING_API % metadata.id)
            Log('Rating JSON ' + rating_json)
            rating_dict = JSON.ObjectFromString(rating_json)
            metadata.rating = float(rating_dict['average']) * 2
            Log('Rating ' + metadata.rating)
        except Exception, e:
            Log('Rating exception ' + str(e))
