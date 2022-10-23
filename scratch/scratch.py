#!/usr/bin/python3

import hashlib
import re


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dfs(vec, vis, node, compSize):
    vis[node] = True
    compSize[0] += 1
    for x in vec[node]:
        if not vis[x]:
            dfs(vec, vis, x, compSize)


def minimumSwaps(a, n):
    aux = [*enumerate(a)]
    aux.sort(key=lambda it: it[1])
    vis = [False] * (n + 1)
    vec = [[] for i in range(n + 1)]
    for i in range(n):
        vec[aux[i][0] + 1].append(i + 1)
    ans = 0
    for i in range(1, n + 1):
        compSize = [0]
        if not vis[i]:
            dfs(vec, vis, i, compSize)
            ans += compSize[0] - 1
    return ans


a = [55, 31, 20, 42, 17, 23, 16]
n = len(a)
z = minimumSwaps(a, n)
...


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import copy
import functools

@functools.total_ordering
class MyClass:

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __gt__(self, other):
        return self.name > other.name

a = MyClass('a')
my_list = [a]
dup = copy.copy(my_list)

print('             my_list:', my_list)
print('                 dup:', dup)
print('      dup is my_list:', (dup is my_list))
print('      dup == my_list:', (dup == my_list))
print('dup[0] is my_list[0]:', (dup[0] is my_list[0]))
print('dup[0] == my_list[0]:', (dup[0] == my_list[0]))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import weakref

class ExpensiveObject:

    def __del__(self):
        print('(Deleting {})'.format(self))

obj = ExpensiveObject()
r = weakref.ref(obj)

print('obj:', obj)
print('ref:', r)
print('r():', r())

print('deleting obj')
del obj
print('r():', r())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Priority Queue

import functools
import queue
import threading


@functools.total_ordering
class Job:

    def __init__(self, priority, description):
        self.priority = priority
        self.description = description
        print('New job:', description)
        return

    def __eq__(self, other):
        try:
            return self.priority == other.priority
        except AttributeError:
            return NotImplemented

    def __lt__(self, other):
        try:
            return self.priority < other.priority
        except AttributeError:
            return NotImplemented


q = queue.PriorityQueue()

q.put(Job(3, 'Mid-level job'))
q.put(Job(10, 'Low-level job'))
q.put(Job(1, 'Important job'))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Threaded podcast client

from queue import Queue
import threading
import time
import urllib
from urllib.parse import urlparse

import feedparser

# Set up some global variables
num_fetch_threads = 2
enclosure_queue = Queue()

# A real app wouldn't use hard-coded data...
feed_urls = [
    'http://talkpython.fm/episodes/rss',
]


def message(s):
    print('{}: {}'.format(threading.current_thread().name, s))

# The function download_enclosures() runs in the worker thread and processes the downloads using urllib.


def download_enclosures(q):
    """This is the worker thread function.
    It processes items in the queue one after
    another.  These daemon threads go into an
    infinite loop, and exit only when
    the main thread ends.
    """
    while True:
        message('looking for the next enclosure')
        url = q.get()
        filename = url.rpartition('/')[-1]
        message('downloading {}'.format(filename))
        response = urllib.request.urlopen(url)
        data = response.read()
        # Save the downloaded file to the current directory
        message('writing to {}'.format(filename))
        with open(filename, 'wb') as outfile:
            outfile.write(data)
        q.task_done()

# Once the target function for the threads is defined, the worker threads can be started. When download_enclosures() processes the statement url = q.get(),
# it blocks and waits until the queue has something to return. That means it is safe to start the threads before there is anything in the queue.


# Set up some threads to fetch the enclosures
for i in range(num_fetch_threads):
    worker = threading.Thread(
        target=download_enclosures,
        args=(enclosure_queue,),
        name='worker-{}'.format(i),
    )
    worker.setDaemon(True)
    worker.start()

# The next step is to retrieve the feed contents using the feedparser module and enqueue the URLs of the enclosures. As soon as the first URL is added to
# the queue, one of the worker threads picks it up and starts downloading it. The loop continues to add items until the feed is exhausted, and the worker
# threads take turns dequeuing URLs to download them.

# Download the feed(s) and put the enclosure URLs into the queue.
for url in feed_urls:
    response = feedparser.parse(url, agent='fetch_podcasts.py')
    for entry in response['entries'][:5]:
        for enclosure in entry.get('enclosures', []):
            parsed_url = urlparse(enclosure['url'])
            message('queuing {}'.format(
                parsed_url.path.rpartition('/')[-1]))
            enclosure_queue.put(enclosure['url'])

# The only thing left to do is wait for the queue to empty out again, using join().

# Now wait for the queue to be empty, indicating that we have
# processed all of the downloads.
message('*** main thread waiting')
enclosure_queue.join()
message('*** done')
exit()


def process_job(q):
    while True:
        next_job = q.get()
        print('Processing job:', next_job.description)
        q.task_done()


workers = [
    threading.Thread(target=process_job, args=(q,)),
    threading.Thread(target=process_job, args=(q,)),
]
for w in workers:
    w.setDaemon(True)
    w.start()

q.join()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Enumeration

import enum


class BugStatus(enum.Enum):

    new = (7, ['incomplete',
               'invalid',
               'wont_fix',
               'in_progress'])
    incomplete = (6, ['new', 'wont_fix'])
    invalid = (5, ['new'])
    wont_fix = (4, ['new'])
    in_progress = (3, ['new', 'fix_committed'])
    fix_committed = (2, ['in_progress', 'fix_released'])
    fix_released = (1, ['new'])

    def __init__(self, num, transitions):
        self.num = num
        self.transitions = transitions

    def can_transition(self, new_state):
        return new_state.name in self.transitions


print('Name:', BugStatus.in_progress.name)
print('Value:', BugStatus.in_progress.value)
print('Custom attribute:', BugStatus.in_progress.transitions)
print('Using attribute:',
      BugStatus.in_progress.can_transition(BugStatus.new))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# difflib

text1 = """Lorem ipsum dolor sit amet, consectetuer adipiscing
elit. Integer eu lacus accumsan arcu fermentum euismod. Donec
pulvinar porttitor tellus. Aliquam venenatis. Donec facilisis
pharetra tortor.  In nec mauris eget magna consequat
convalis. Nam sed sem vitae odio pellentesque interdum. Sed
consequat viverra nisl. Suspendisse arcu metus, blandit quis,
rhoncus ac, pharetra eget, velit. Mauris urna. Morbi nonummy
molestie orci. Praesent nisi elit, fringilla ac, suscipit non,
tristique vel, mauris. Curabitur vel lorem id nisl porta
adipiscing. Suspendisse eu lectus. In nunc. Duis vulputate
tristique enim. Donec quis lectus a justo imperdiet tempus."""

text1_lines = text1.splitlines()

text2 = """Lorem ipsum dolor sit amet, consectetuer adipiscing
elit. Integer eu lacus accumsan arcu fermentum euismod. Donec
pulvinar, porttitor tellus. Aliquam venenatis. Donec facilisis
pharetra tortor. In nec mauris eget magna consequat
convalis. Nam cras vitae mi vitae odio pellentesque interdum. Sed
consequat viverra nisl. Suspendisse arcu metus, blandit quis,
rhoncus ac, pharetra eget, velit. Mauris urna. Morbi nonummy
molestie orci. Praesent nisi elit, fringilla ac, suscipit non,
tristique vel, mauris. Curabitur vel lorem id nisl porta
adipiscing. Duis vulputate tristique enim. Donec quis lectus a
justo imperdiet tempus.  Suspendisse eu lectus. In nunc."""

text2_lines = text2.splitlines()

# difflib_differ.py

import difflib
# from difflib_data import *

d = difflib.Differ()
diff = d.compare(text1_lines, text2_lines)
# print('\n'.join(diff))

# difflib_unified.py

import difflib
# from difflib_data import *

diff = difflib.unified_diff(
    text1_lines,
    text2_lines,
    lineterm='',
)
print('\n'.join(diff))

...


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLOSURES

def f(x):
    def g(y):
        return x + y
    return g  # Return a closure.


def h(x):
    return lambda y: x + y  # Return a closure.


# Assigning specific closures to variables.
a = f(1)
b = h(1)

# Using the closures stored in variables.
assert a(5) == 6
assert b(5) == 6

# Using closures without binding them to variables first.
assert f(1)(5) == 6  # f(1) is the closure.
assert h(1)(5) == 6  # h(1) is the closure.


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
with open("/var/log/syslog") as f:
    for line in f:
        encoded =line.encode()
        hashval = hashlib.sha512(encoded)
        print(hashval.hexdigest())




def test_patterns(text, patterns):
    """Given source text and a list of patterns, look for
    matches for each pattern within the text and print
    them to stdout.
    """
    # Look for each pattern in the text and print the results
    for pattern, desc in patterns:
        print("'{}' ({})\n".format(pattern, desc))
        print("  '{}'".format(text))
        for match in re.finditer(pattern, text):
            s = match.start()
            e = match.end()
            substr = text[s:e]
            n_backslashes = text[:s].count('\\')
            prefix = '.' * (s + n_backslashes)
            print("  {}'{}'".format(prefix, substr))
        print()
    return


if __name__ == '__main__':
    test_patterns('abbaaabbbbaaaaa',
                  [('ab', "'a' followed by 'b'"),
                   ])


text = 'abbaaabbbbaaaaa'

pattern = 'ab'

for match in re.findall(pattern, text):
    print('Found {!r}'.format(match))
    print('Found {}'.format(match))
    ...

"""
FROM: http://www.diveintopython3.net/generators.html#a-list-of-functions

Defining separate named functions for each match and apply rule isn’t really necessary. You never call them directly;
you add them to the rules sequence and call them through there. Furthermore, each function follows one of two patterns.
All the match functions call re.search(), and all the apply functions call re.sub(). Let’s factor out the patterns so
that defining new rules can be easier.
"""


def build_match_and_apply_functions(pattern, search, replace):
    ...

    def matches_rule(word):
        return re.search(pattern, word)

    def apply_rule(word):
        return re.sub(search, replace, word)

    return matches_rule, apply_rule


"""
build_match_and_apply_functions() is a function that builds other functions dynamically. It takes pattern, search and
replace, then defines a matches_rule() function which calls re.search() with the pattern that was passed to the
build_match_and_apply_functions() function, and the word that was passed to the matches_rule() function you’re building.
Whoa.

Building the apply function works the same way. The apply function is a function that takes one parameter, and calls
re.sub() with the search and replace parameters that were passed to the build_match_and_apply_functions() function, and
the word that was passed to the apply_rule() function you’re building. This technique of using the values of outside
parameters within a dynamic function is called closures. You’re essentially defining constants within the apply
function you’re building: it takes one parameter (word), but it then acts on that plus two other values (search and
replace) which were set when you defined the apply function.

Finally, the build_match_and_apply_functions() function returns a tuple of two values: the two functions you just
created. The constants you defined within those functions (pattern within the matches_rule() function, and search and
replace within the apply_rule() function) stay with those functions, even after you return from
build_match_and_apply_functions(). That’s insanely cool.

If this is incredibly confusing (and it should be, this is weird stuff), it may become clearer when you see how to use it.
"""


patterns = \
  (
    (r'[sxz]$',           r'$',  r'es'),
    (r'[^aeioudgkprt]h$', r'$',  r'es'),
    (r'(qu|[^aeiou])y$',  r'y$', r'ies'),
    (r'$',                r'$',  r's')
  )

rules = [build_match_and_apply_functions(pattern, search, replace)
         for (pattern, search, replace) in patterns]

"""
Our pluralization “rules” are now defined as a tuple of tuples of strings (not functions). The first string in each
group is the regular expression pattern that you would use in re.search() to see if this rule matches. The second and
third strings in each group are the search and replace expressions you would use in re.sub() to actually apply the
rule to turn a noun into its plural.

There’s a slight change here, in the fallback rule. In the previous example, the match_default() function simply
returned True, meaning that if none of the more specific rules matched, the code would simply add an s to the end of
the given word. This example does something functionally equivalent. The final regular expression asks whether the
word has an end ($ matches the end of a string). Of course, every string has an end, even an empty string, so this
expression always matches. Thus, it serves the same purpose as the match_default() function that always returned True:
it ensures that if no more specific rule matches, the code adds an s to the end of the given word.

This line is magic. It takes the sequence of strings in patterns and turns them into a sequence of functions. How? By
“mapping” the strings to the build_match_and_apply_functions() function. That is, it takes each triplet of strings and
calls the build_match_and_apply_functions() function with those three strings as arguments. The
build_match_and_apply_functions() function returns a tuple of two functions. This means that rules ends up being
functionally equivalent to the previous example: a list of tuples, where each tuple is a pair of functions. The first
function is the match function that calls re.search(), and the second function is the apply function that calls re.sub().
"""

"""
Rounding out this version of the script is the main entry point, the plural() function.
"""


def plural(noun):
    for matches_rule, apply_rule in rules:
        if matches_rule(noun):
            return apply_rule(noun)


if __name__ == '__main__':
    words = ['hose', 'cow', 'lash', 'thought', 'hippopotamus']
    for new_word in words:
        pluralized = plural(new_word)
        ...
...


"""
Since the rules list is the same as the previous example (really, it is), it should come as no surprise that the
plural() function has not changed at all. It’s completely generic; it takes a list of rule functions and calls them in
order. It does not care how the rules are defined. In the previous example, they were defined as separate named
functions. Now they are built dynamically by mapping the output of the build_match_and_apply_functions() function onto
a list of raw strings. It does not matter; the plural() function still works the same way. 
"""
