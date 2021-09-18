from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import django.db.utils
from speechdb.models import Author, Work, Character, CharacterInstance, Speech, SpeechCluster
import csv
import os
import re
from django.core import serializers


def validate(s, choices, default=None, allow_none=False):
    '''Validate user input'''
    
    if s is not None:
        s = str(s).strip().lower()
        if len(s) == 0:
            s = None
    
    allowed = choices.values
    if allow_none:
        allowed.append(None)
    
    if s not in allowed:
        s = default.value
    
    return s


def addAuthors(file):
    '''Parse the authors list from a TSV file'''
    f = open(file)
    reader = csv.DictReader(f, delimiter='\t')
        
    for rec in reader:
        a = Author()
        a.id = int(rec.get('id').strip())
        a.name = rec.get('name').strip()
        a.wd = rec.get('wd').strip()
        a.urn = rec.get('urn').strip()
        a.save()


def addWorks(file):
    '''Parse the works list from a TSV file'''
    f = open(file)
    reader = csv.DictReader(f, delimiter='\t')
    
    for rec in reader:
        w = Work()
        w.id = int(rec.get('id').strip())
        auth_id = rec.get('author').strip()
        try:
            w.author = Author.objects.get(id=int(auth_id))
        except:
            print(f'Skipping work {w.id}: Can\'t parse author id "{auth_id}".')
            continue
        w.title = rec.get('title').strip()
        w.lang = rec.get('lang').strip()
        w.wd = rec.get('wd').strip()
        w.urn = rec.get('urn').strip()
        w.save()


def addChars(file):
    '''Parse the characters list from a TSV file'''
    f = open(file)
    reader = csv.DictReader(f, delimiter='\t')
    
    # a container for anonymous instances and alternate identities
    characters = {}
    alt_chars = {}
    anon_chars = {}
    
    for rec in reader:
        c = Character()
        c.name = rec.get('name').strip() or None
        if c.name is None:
            print(f'Character {c.id} has no name. Skipping')
            continue
        if c.name == 'self':
            continue
        if len(Character.objects.filter(name=c.name)) > 0:
            print(f'Adding duplicate char name {c.name}.')
        c.wd = rec.get('wd').strip() or None
        c.manto = rec.get('manto').strip() or None
        c.anon = (rec.get('anon') is not None) and (
                    len(rec.get('anon').strip()) > 0)
        c.being = validate(rec.get('being'), Character.CharacterBeing,
                    default=Character.CharacterBeing.MORTAL)
        c.number = validate(rec.get('number'), Character.CharacterNumber,
                    default=Character.CharacterNumber.INDIVIDUAL)
        c.gender = validate(rec.get('gender'), Character.CharacterGender,
                    default=Character.CharacterGender.NA)
        c.same_as = rec.get('same_as').strip() or None
        c.notes = rec.get('notes').strip() or None
        
        c.tags = {}
        for col in rec.keys():
            if col.startswith('tag_'):
                key = col[4:]
                vals = []
                for tag in rec.get(col).split(','):
                    tag = tag.strip()
                    if tag != '':
                        vals.append(tag)
                if len(vals) > 0:
                    c.tags[key] = vals
        
        if c.being is None:
            print(f'Character {c} has no being')
        
        if c.name in characters or c.name in alt_chars or c.name in anon_chars:
            print(f'Multiple records for name {c.name}!')
        
        if c.same_as is not None:
            alt_chars[c.name] = c
        elif c.anon:
            anon_chars[c.name] = c
        else:
            characters[c.name] = c
            c.save()
            
    return characters, alt_chars, anon_chars

    
def addInst(name, speech, characters, alt_chars={}, anon_chars={}):
    '''get or create character instance'''
    
    # details of this instance
    instance_params = {
        'name': name,
        'context': speech.work.title,
    }

    # look for the name in characters list, alt ids, anonymous chars
    if name in characters:
        c = characters[name]
        instance_params['name'] = c.name
        instance_params['gender'] = c.gender
        instance_params['being'] = c.being
        instance_params['number'] = c.number
        instance_params['char'] = c
    elif name in alt_chars:
        c = alt_chars[name]
        instance_params['name'] = c.name
        instance_params['gender'] = c.gender
        instance_params['being'] = c.being
        instance_params['number'] = c.number
        try:
            instance_params['char'] = characters[c.same_as]
        except KeyError:
            print(f'Pseud {name} points to non-existent char {same_as}!'.format(
                    name=name, same_as=alt_chars[name].same_as))
            raise
    elif name in anon_chars:
        c = anon_chars[name]
        instance_params['name'] = c.name
        instance_params['gender'] = c.gender
        instance_params['being'] = c.being
        instance_params['number'] = c.number
        instance_params['anon'] = c.anon
        instance_params['tags'] = c.tags
    else:
        print(f'Failed to find character {name}!')
        return None
    
    #print(f'DEBUG: speech={speech}; params={instance_params}')
    inst, created = CharacterInstance.objects.get_or_create(**instance_params)
    
    return inst


def addSpeeches(file, characters, alt_chars={}, anon_chars={}):
    '''Parse the speeches list from a TSV file'''
    f = open(file)
    reader = csv.DictReader(f, delimiter='\t')
    
    skipped = []
    
    for rec in reader:
        s = Speech()
        errs = []
        
        # seq
        try:
            s.seq = int(rec.get('seq').strip())
        except:
            errs.append('seq')

        # locus
        try:
            book_fi = rec.get('from_book').strip()
            assert book_fi != ''
        except:
            errs.append('from_book')

        try:
            line_fi = rec.get('from_line').strip()
            assert line_fi != ''
        except:
            errs.append('from_line')
        
        try:
            book_la = rec.get('to_book').strip()
            assert book_la != ''
        except:
            errs.append('to_book')

        try:
            line_la = rec.get('to_line').strip()
            assert line_la != ''
        except:
            errs.append('to_line')
    
        s.l_fi = f'{book_fi}.{line_fi}'
        s.l_la = f'{book_la}.{line_la}'
        
        # work
        try:
            s.work = Work.objects.get(id=int(rec.get('work_id')))
        except:
            errs.append('work')

        # cluster type
        try:
            s.type = rec.get('simple_cluster_type')[0].upper()
            assert s.type != ''
        except:
            errs.append('simple_cluster_type')
            # temp value: speech should be deleted
            s.type='M'
        
        # cluster_id
        try:
            cluster_id = int(rec.get('cluster_id').strip())
            s.cluster, created = SpeechCluster.objects.get_or_create(id=cluster_id)
        except:
            errs.append('cluster_id')
            # temp value: speech should be deleted
            s.cluster, created = SpeechCluster.objects.get_or_create(id=999999)

        # cluster part
        try:
            part = rec.get('cluster_part').strip()
            if 'or' in part:
                m = re.search('\d+', part)
                if m:
                    part = m.group(0)
            s.part = int(part)
        except:
            errs.append('part')
            # temp value: speech should be deleted
            s.part = 1
            
        # speech must be saved before adding character instances
        s.save()
        
        # speakers
        try:
            spkr_str = rec.get('speaker').strip()
            assert spkr_str != ''

            for name in spkr_str.split(' and '):
                inst = addInst(name, s, characters=characters, 
                        alt_chars=alt_chars, anon_chars=anon_chars)
                if inst is not None:
                    s.spkr.add(inst)
            assert len(s.spkr.all()) > 0
        except:
            errs.append('speaker')
        
        # speaker notes
        s.spkr_notes = rec.get('speaker_notes').strip() or None

        # addressees
        try:
            addr_str = rec.get('addressee').strip()
            assert addr_str != ''

            for name in addr_str.split(' and '):
                if name == 'self':
                    inst = s.spkr.first()
                else:
                    inst = addInst(name, s, characters=characters,
                            alt_chars=alt_chars, anon_chars=anon_chars)
                if inst is not None:
                    s.addr.add(inst)
            assert len(s.addr.all()) > 0
        except:
            errs.append('addressee')

        # addressee notes
        s.addr_notes = rec.get('addressee_notes').strip() or None
        
        # embeddedness
        try:
            s.level = int(rec.get('embedded_level').strip())
        except:
            errs.append('embedded_level')
        
        # general notes
        s.notes = rec.get('misc_notes').strip() or None
        
        # save speech or log errors
        if len(errs) == 0:
            s.save()
        else:
            skipped.append((reader.line_num, str(s), errs))
            s.delete()
    
    if len(skipped) > 0:
        print(f'skipped {len(skipped)} rows:')
        for line_num, speech, errs in skipped:
            print(line_num, speech, errs)


class Command(BaseCommand):
    help = 'Check data integrity?'
    
    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
    
    def handle(self, *args, **options):
        path = options['path']

        # authors
        auth_file = os.path.join(path, 'authors')
        self.stderr.write(f'Reading data from {auth_file}')
        addAuthors(auth_file)

        # works
        work_file = os.path.join(path, 'works')
        self.stderr.write(f'Reading data from {work_file}')
        addWorks(work_file)

        # characters
        char_file = os.path.join(path, 'characters')
        self.stderr.write(f'Reading data from {char_file}')
        characters, alt_chars, anon_chars = addChars(char_file)

        # speeches, clusters, and char instances
        speech_files = [os.path.join(path, f) for f in sorted(os.listdir(path))
                        if f.startswith('speeches')]
        for speech_file in speech_files:
            self.stderr.write(f'Reading data from {speech_file}')
            addSpeeches(speech_file, characters=characters, alt_chars=alt_chars,
                        anon_chars=anon_chars)