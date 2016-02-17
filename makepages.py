#
# Copyright (C) Stanislaw Adaszewski, 2016
# http://algoholic.eu
#
# Generate printout of MtG cards based on a deck list
# and directory containing images.
#

from argparse import ArgumentParser
from PIL import Image
import os
import random


def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]


def create_parser():
	parser = ArgumentParser()
	parser.add_argument('card_list', type=str)
	parser.add_argument('--dpi', type=int, default=300)
	parser.add_argument('--card_dir', type=str, default='cards')
	parser.add_argument('--page_width_mm', type=int, default=210)
	parser.add_argument('--page_height_mm', type=int, default=297)
	parser.add_argument('--page_margin_mm', type=int, default=9)
	parser.add_argument('--spacing_mm', type=int, default=1)
	return parser
	
	
def main():
	parser = create_parser()
	args = parser.parse_args()
	with open(args.card_list, 'rb') as f:
		lines = filter(lambda y: y != '',
			map(lambda x: x.strip(), f.read().split('\n')))
	cards = os.listdir(args.card_dir)
	# print cards[0]
	im = Image.open(os.path.join(args.card_dir, cards[0]))
	print 'card dimensions (px):', im.size
	card_size = im.size
	dpmm = args.dpi / 25.441
	page_size = (int(dpmm * args.page_width_mm),
		int(dpmm * args.page_height_mm))
	print 'page_size:', page_size
	page = Image.new('RGB', page_size)
	page.paste(0xffffffff, (0, 0, page_size[0], page_size[1]))
	page_margin = int(args.page_margin_mm * dpmm)
	spacing = int(args.spacing_mm * dpmm)
	ofs_x = ofs_y = page_margin
	page_cnt = 0
	for l in lines:
		if l.startswith('#'): continue # comment
		l = l.split(' ')
		(cnt, name) = int(l[0]), ' '.join(l[1:])
		print 'cnt:', cnt, 'name:', name
		L = map(lambda x: levenshtein(x, name), cards)
		# print L
		# idx = L.index(min(L))
		closest = min(L)
		# print 'closest:', closest
		indices = [i for i, x in enumerate(L) if x == closest]
		# print 'indices:',indices
		# print idx, L[idx]
		# print 'fname:', fname
		# return
		
		for i in xrange(cnt):
			fname = cards[indices[random.randint(0, len(indices) - 1)]]
			im = Image.open(os.path.join(args.card_dir, fname))
			if im.size != card_size:
				print 'WARNING: resizing', fname, 'from', im.size, \
					'to', card_size
				im = im.resize(card_size)
				
			if ofs_x + card_size[0] + page_margin > page_size[0]:
				ofs_x = page_margin
				ofs_y += card_size[1] + spacing
				if ofs_y + card_size[1] + page_margin > page_size[1]:
					page.save('page_%d.png' % page_cnt)
					page_cnt += 1
					ofs_y = page_margin
					page.paste(0xffffffff, (0, 0,
						page_size[0], page_size[1]))
			
			page.paste(im, (ofs_x, ofs_y,
				ofs_x + im.size[0], ofs_y + im.size[1]))
			ofs_x += im.size[0] + spacing
			# ofs_y += im.size[1]
	page.save('page_%d.png' % page_cnt)
	
	
if __name__ == '__main__':
	main()
