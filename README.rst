Captcha onion broad crawl
=========================

Usage: get an ``OnionList.csv`` file in the following format
(onion domain is without ``.onion``, second column is port number,
and the last is ignored)::

    oniondomainhere,80,1462950051

Run spider::

    scrapy crawl spider -s SPLASH_URL=splash_url -o out/out.csv -s LOG_FILE=out/out.log

It will search for captchas (the check is just ``'captcha' in body.lower()``)
and save screenshots to ``out/screenshots``, and html to
``out/html``, writing ``item_id`` into the specified output file
(you can use this ``item_id`` to match filenames with urls).
Depth limit is 2 by default, and it crawls no more then 100 pages from each
domain, stopping once it has found a captcha.

Adjust concurrency settings according to the splash cluster size, current work
best for 12 splash processes.

License is MIT.
