import pygame as pg
import sys,os
from pygame.locals import *
import time
from random import randint
from math import sqrt
mainClock = pg.time.Clock()
pg.init()
info=pg.display.Info()#You have to call this before pygame.display.set_mode()
sizeFull=info.current_w,info.current_h
#size=(sizeFull[0],sizeFull[1]-30)

size=wx,wy=320,240
pxsz=4
sizeW=wx*pxsz,wy*pxsz
win=pg.Surface(size)
winW=pg.display.set_mode(sizeW, RESIZABLE)
#win=pg.display.set_mode(sizeFull,pg.FULLSCREEN)
#os.environ['SDL_VIDEO_CENTERED']='1'# You have to call this before pygame.init()
worldsize=100
cellsize=10
world=[[randint(
	int(sqrt((i-worldsize//2)**2+(j-worldsize//2)**2)/(worldsize//8)),
	int(sqrt((i-worldsize//2)**2+(j-worldsize//2)**2)/(worldsize//20)))
 	for j in range(worldsize)] for i in range(worldsize)]
for x in range(worldsize):
	for y in range(worldsize):
			if world[x][y]>4:
				world[x][y]=4
for x in range(10):
	world[worldsize//2-5+x][worldsize//2+1]=1
light=[[randint(0,4) for j in range(worldsize)] for i in range(worldsize)]
roots=[[[1 if randint(0,100)==0 else 0 for k in range(8)] for j in range(worldsize)] for i in range(worldsize)]
rootsrgn=[[[randint(0,10) for k in range(2)] for j in range(worldsize+1)] for i in range(worldsize+1)]

rootmods=[#1 - middle of cell 2 - corner of cell
[[0,0],[2,2]],
[[0,2],[2,0]],
[[1,0],[1,2]],
[[0,1],[2,1]],

[[0,1],[1,2]],
[[1,2],[2,1]],
[[0,1],[1,2]],
[[1,2],[2,1]]]

neighbours=[#rootId[[firstEnd[nnbrCoords,nbrRootIds]][secondEnd[-,-]]]
[],
[],
[[[0,1],[2,6,7]],[[0,-1],[2,4,5]]],#2
[[[-1,0],[3,5,7]],[[1,0],[3,4,6]]],#3
[[[-1,0],[3,5,7]],[[0,-1],[2,4,5]]],#4
[[[0,1],[2,6,7]],[[1,0],[3,4,6]]],#5
[[[-1,0],[3,5,7]],[[1,0],[3,4,6]]],#6
[[[-1,0],[3,5,7]],[[0,-1],[2,4,5]]]]

def rootslv(x,y,axis,pos,r):
	if r==0:
		return 0
	elif r==2:
		return cellsize
	else:
		return rootsrgn[x][y][axis]

world[1][1]=0
pos=0
framerate=60

tile=pg.image.load('tile10.png').convert()
tiler=pg.image.load('tiler10.png').convert()
tileg=pg.image.load('tileg10.png').convert()
tileb=pg.image.load('tileb10.png').convert()
sphere=pg.image.load('sphere.png').convert_alpha()
walkfiles=['frog40w1.png','frog40w2.png','frog40s.png','frog40p.png','frog40h.png']
frogframes=[pg.image.load(n).convert_alpha() for n in walkfiles]
l=len(frogframes)
for i in range(l):
	frogframes.append(pg.transform.flip(frogframes[i],True,False))

wind=pg.mixer.music.load('wind.ogg')
pg.mixer.music.play(-1)
burpsnd=pg.mixer.Sound('burp.ogg')
crumblesnd=pg.mixer.Sound('crumble.ogg')
hacksnd=pg.mixer.Sound('hack.ogg')
rootsgrowsnd=pg.mixer.Sound('rootsgrow.ogg')
rootsgrowsnd.play()
shleptsnd=pg.mixer.Sound('shlept.ogg')

agent=[worldsize*cellsize//2,worldsize*cellsize//2]
agentv=[0,0]
camera=[worldsize*cellsize//2,worldsize*cellsize//2]
lights=[[worldsize//2,worldsize//2+5,255]]
bombcool=0
gravity=1
tilestoggle=True
rootstoggle=True
walking=False
falling=False
agentspeedx=3
left=True
puking=False
jumping=False
jumpcool=0
pukecool=0
hacking=False
hackcool=0
walkingFrame=0
frameTimer=10
lasttime=time.time()
debug=False
rootgrowcnt=0
running=True

#make starting cave
agentcell=[int(agent[0]//cellsize),int(agent[1]//cellsize)+4]
'''
bombrad=5
bombsize=bombrad
for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
	for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
		if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
			if randint(0,1)==0:
				world[x][y]-=1
			if world[x][y]<0:
				world[x][y]=0
bombsize=bombrad-1
for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
	for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
		if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
			if randint(0,1)==0:
				world[x][y]-=1
			if world[x][y]<0:
				world[x][y]=0
bombsize=bombrad-2
for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
	for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
		if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
			if randint(0,1)==0:
				world[x][y]-=1
			if world[x][y]<0:
				world[x][y]=0
bombsize=bombrad-3
for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
	for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
		if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
			world[x][y]=0
'''
while running:
	for event in pg.event.get():
		if event.type==pg.QUIT:
			running=False
		elif event.type==VIDEORESIZE:
			size=event.dict['size']
			screen=pg.display.set_mode(size,HWSURFACE|DOUBLEBUF|RESIZABLE)
		elif event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				running=False
			if event.key == pg.K_RETURN and pg.key.get_mods() & pg.KMOD_SHIFT:
				pg.display.set_caption('pressed: SHIFT + A ')
				print("pressed: SHIFT + K_RETURN")
				if fullScr:
					screen=pg.display.set_mode(size, RESIZABLE)
					fullScr=False
				else:
					pg.display.set_mode(sizeFull,pg.FULLSCREEN)
					fullScr=True
				sleep(1)

	mb1,mb2,mb3=pg.mouse.get_pressed()
	mx,my=pg.mouse.get_pos()
	dt=time.time()-lasttime
	dt*=60
	lasttime=time.time()

	if rootgrowcnt<150:
		rootgrowcnt+=1
		for x in range(worldsize):
			for y in range(worldsize):
				for i in range(2,8):
					#neighbours=[#rootId[[firstEnd[nnbrCoords,nbrRootIds]][secondEnd[-,-]]]
					if roots[x][y][i]==1 and randint(0,10)==0:
						for nbr,rts in neighbours[i]:
							for r in rts:
								if randint(0,7)==0:
									if x+nbr[0]>0 and x+nbr[0]<worldsize-1 and y+nbr[1]>0 and y+nbr[1]<worldsize-1:
										roots[x+nbr[0]][y+nbr[1]][r]=1


	keys=pg.key.get_pressed()

	if keys[K_a]:
		agentv[0]-=1
		if agentv[0]<-agentspeedx:
			agentv[0]=-agentspeedx
		left=True
	elif keys[K_d]:
		agentv[0]+=agentspeedx
		if agentv[0]>agentspeedx:
			agentv[0]=agentspeedx
		left=False
	else:
		if agentv[0]>0:
			agentv[0]-=1
		if agentv[0]<0:
			agentv[0]+=1
	'''
	elif keys[K_w]:
		agent[1]-=agentspeedx
	elif keys[K_s]:
		agent[1]+=agentspeedx
		'''
	if keys[K_SPACE] and not falling:
		jumping=True

	if debug:
		if keys[K_UP]:
			agent[1]-=100
		if keys[K_DOWN]:
			agent[1]+=100
		if keys[K_LEFT]:
			agent[0]-=100
		if keys[K_RIGHT]:
			agent[0]+=100
		if keys[K_t]:
			if tilestoggle:
				tilestoggle=False
			else:
				tilestoggle=True
		if keys[K_r]:
			if rootstoggle:
				rootstoggle=False
			else:
				rootstoggle=True
		if keys[K_z]:
			if gravity==0:
				gravity=1
			else:
				gravity=0
	if keys[K_e]:
		if hackcool<=0:
			hacksnd.play()
			hackcool=10
			if left:
				lm=-1
			else:
				lm=1
			agentcell=[int(agent[0]//cellsize+lm),int(agent[1]//cellsize)+4]
			bombrad=2
			bombsize=bombrad
			hitcnt=0
			for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
				for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
					if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
						if world[x][y]>0:
							hitcnt+=1
						if randint(0,1)==0:
							world[x][y]-=1
						if world[x][y]<0:
							world[x][y]=0
			crumblesnd.play()
			bombsize=bombrad-1
			for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
				for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
					if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
						if randint(0,1)==0:
							world[x][y]-=1
						if world[x][y]<0:
							world[x][y]=0
			bombsize=bombrad-2
			for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
				for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
					if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
						if randint(0,1)==0:
							world[x][y]-=1
						if world[x][y]<0:
							world[x][y]=0
	if keys[K_q]:
		if pukecool<=0:
			burpsnd.play()
			pukecool=10
			if left:
				lm=-1
			else:
				lm=1
			agentcell=[int(agent[0]//cellsize)+lm,int(agent[1]//cellsize)+5]
			if not agentcell in lights:
				lights.append(agentcell+[100])
	if keys[K_x] and debug:
		if bombcool<=0:
			bombcool=10
			agentcell=[int(agent[0]//cellsize),int(agent[1]//cellsize)+3]
			bombrad=4
			bombsize=bombrad
			for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
				for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
					if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
						if randint(0,1)==0:
							world[x][y]-=1
						if world[x][y]<0:
							world[x][y]=0
			bombsize=bombrad-1
			for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
				for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
					if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
						if randint(0,1)==0:
							world[x][y]-=1
						if world[x][y]<0:
							world[x][y]=0
			bombsize=bombrad-2
			for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
				for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
					if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
						if randint(0,1)==0:
							world[x][y]-=1
						if world[x][y]<0:
							world[x][y]=0
			bombsize=bombrad-3
			for x in range(agentcell[0]-bombsize,agentcell[0]+bombsize):
				for y in range(agentcell[1]-bombsize-5,agentcell[1]+bombsize-5):
					if x>0 and x<worldsize-1 and y>0 and y<worldsize-1:
						world[x][y]=0

	if bombcool>0:
		bombcool-=dt
	if hackcool>0:
		hacking=True
		hackcool-=dt
	else:
		hacking=False
	if pukecool>0:
		puking=True
		pukecool-=dt
	else:
		puking=False
	#frog falling
	agentcellf=[int(agent[0]//cellsize),int((agent[1])//cellsize)+1]#cell below
	if world[agentcellf[0]][agentcellf[1]]==0 and not jumping:#hitbox
		falling=True
		if agentv[1]<5:
			agentv[1]+=gravity
	else:
		#agentv[1]=0
		falling=False
	if falling:
		agent[1]+=agentv[1]
		agentcell=[int(agent[0]//cellsize),int(((agent[1])-4)//cellsize)]
		#if world[agentcell[0]][agentcell[1]]!=0 and agentcellf[0]>=0 and agentcellf[0]<worldsize-1 and agentcellf[1]>=0 and agentcellf[1]<worldsize-1:
			#falling=False
			#agent[1]=(agentcell[1])*cellsize
			#agentv[1]=0
	#frog jumping
	if jumping:
		if agentv[1]>0:
			agentv[1]=-1
		agentv[1]-=2
		agent[1]+=agentv[1]
		if agentv[1]<-6:
			jumping=False
			falling=True
		agentcellf=[int(agent[0]//cellsize),int((agent[1])//cellsize)-3]#cell above
		if world[agentcellf[0]][agentcellf[1]]!=0:#hitbox
			agentv[1]=1
			jumping=False
			falling=True


	#frog walking
	agent[0]+=agentv[0]
	if abs(agentv[0])>0:
		walking=True
	else:
		walking=False
	if walking:

		frameTimer-=dt
		if frameTimer<=0:
			shleptsnd.play()
			frameTimer=10
			walkingFrame+=1
			if walkingFrame>1:
				walkingFrame=0
	#frog colide
	agentcell=[int(agent[0]//cellsize),int((agent[1])//cellsize)]
	if world[agentcell[0]][agentcell[1]]!=0:
		agent[0]-=agentv[0]
		agentv[0]=0
	#clip player to map
	if agent[0]<0:
		agent[0]=0
	if agent[0]>(worldsize-1)*cellsize:
		agent[0]=(worldsize-1)*cellsize
	if agent[1]<0:
		agent[1]=0
	if agent[1]>(worldsize-1)*cellsize:
		agent[1]=(worldsize-1)*cellsize
	#camera follow
	if camera[0]!=agent[0]:
		camera[0]+=int((agent[0]-camera[0])/10*dt)
	if camera[1]!=agent[1]:
		camera[1]+=int((agent[1]-camera[1])/10*dt)

	agentcell=[int(agent[0]//cellsize),int((agent[1])//cellsize)]#cell below 1px
	cw=(255,255,255)
	cr=(255,0,0)
	cg=(0,255,0)
	cb=(0,0,255)

	win.fill((255,255,255))
	#calculate camera stats
	cameracell=[int(camera[0]//cellsize),int(camera[1]//cellsize)]
	vizcellsx=17
	vizcellsy=16
	vizcellsxmin=cameracell[0]-vizcellsx
	if vizcellsxmin<0:vizcellsxmin=0
	vizcellsxmax=cameracell[0]+vizcellsx
	if vizcellsxmax>worldsize-1:vizcellsxmax=worldsize-1
	vizcellsymin=cameracell[1]-vizcellsy
	if vizcellsymin<0:vizcellsymin=0
	vizcellsymax=cameracell[1]+vizcellsy
	if vizcellsymax>worldsize-1:vizcellsymax=worldsize-1
	#calculate light
	lightfalloff=30
	for x in range(vizcellsxmin,vizcellsxmax):
		for y in range(vizcellsymin,vizcellsymax):
			light[x][y]=0
	for i,lght in enumerate(lights):
		if lght[2]<200:
			lights[i][2]+=5
		if lght[0]>=vizcellsxmin and lght[0]<vizcellsxmax and lght[1]>=vizcellsymin and lght[1]<vizcellsymax:
			light[lght[0]][lght[1]-5]=lght[2]
	#light[agentcell[0]][agentcell[1]-7]=200
	for x in range(vizcellsxmin,vizcellsxmax):
		for y in range(vizcellsymin,vizcellsymax):
			lightnbr=[]
			for xm in [-1,0,1]:
				for ym in [-1,0,1]:
					xc=x+xm
					yc=y+ym
					if xc>0 and xc<worldsize-1 and yc>0 and yc<worldsize-1:
						if abs(xm)+abs(ym)==2:
							lightnbr.append(int(light[xc][yc]-lightfalloff*1.4))
						else:
							lightnbr.append(light[xc][yc]-lightfalloff)
			pret=max(lightnbr)
			if light[x][y]<pret:
				light[x][y]=pret
	for x in range(vizcellsxmax-vizcellsxmin):
		for y in range(vizcellsymax-vizcellsymin):
			lightnbr=[]
			for xm in [-1,0,1]:
				for ym in [-1,0,1]:
					xc=vizcellsxmax-x+xm
					yc=vizcellsymax-y+ym
					if xc>0 and xc<worldsize-1 and yc>0 and yc<worldsize-1:
						if abs(xm)+abs(ym)==2:
							lightnbr.append(int(light[xc][yc]-lightfalloff*1.4))
						else:
							lightnbr.append(light[xc][yc]-lightfalloff)
			pret=max(lightnbr)
			if light[vizcellsxmax-x][vizcellsymax-y]<pret:
				light[vizcellsxmax-x][vizcellsymax-y]=pret
	#draw light
	for x in range(vizcellsxmin,vizcellsxmax):
		for y in range(vizcellsymin,vizcellsymax):
			pos=(x*cellsize-camera[0]+wx//2,y*cellsize-camera[1]+wx//2)
			#if world[x][y]==1:
			rct=(pos[0],pos[1],cellsize,cellsize)
			c=light[x][y]
			clr=(c,c/1.1,c/1.5+55)
			pg.draw.rect(win,clr,rct)

	#draw tiles
	if tilestoggle:
		for x in range(vizcellsxmin,vizcellsxmax):
			for y in range(vizcellsymin,vizcellsymax):
				pos=(x*cellsize-camera[0]+wx//2,y*cellsize-camera[1]+wx//2)
				if world[x][y]==1:
					win.blit(tile,pos)
				elif world[x][y]==2:
					win.blit(tiler,pos)
				elif world[x][y]==3:
					win.blit(tileg,pos)
				elif world[x][y]==4:
					win.blit(tileb,pos)
	#draw pukes
	for lght in lights:
		if lght[0]>=vizcellsxmin and lght[0]<vizcellsxmax and lght[1]>=vizcellsymin and lght[1]<vizcellsymax:
			pos=(lght[0]*cellsize-camera[0]+wx//2,(lght[1]-5)*cellsize-camera[1]+wx//2)
			win.blit(sphere,pos)


	if walking:
		if left:
			win.blit(frogframes[walkingFrame+5],[agent[0]-14-camera[0]+wx//2,agent[1]-30-camera[1]+wx//2])
		else:
			win.blit(frogframes[walkingFrame],[agent[0]-14-camera[0]+wx//2,agent[1]-30-camera[1]+wx//2])
	elif puking:
		if left:
			win.blit(frogframes[3+5],[agent[0]-14-camera[0]+wx//2,agent[1]-30-camera[1]+wx//2])
		else:
			win.blit(frogframes[3],[agent[0]-14-camera[0]+wx//2,agent[1]-30-camera[1]+wx//2])
	elif hacking:
		if left:
			win.blit(frogframes[4+5],[agent[0]-14-camera[0]+wx//2,agent[1]-30-camera[1]+wx//2])
		else:
			win.blit(frogframes[4],[agent[0]-14-camera[0]+wx//2,agent[1]-30-camera[1]+wx//2])
	else:
		if left:
			win.blit(frogframes[2+5],[agent[0]-14-camera[0]+wx//2,agent[1]-30-camera[1]+wx//2])
		else:
			win.blit(frogframes[2],[agent[0]-14-camera[0]+wx//2,agent[1]-30-camera[1]+wx//2])
	#draw roots
	rootsrgn
	if rootstoggle:
		for x in range(vizcellsxmin,vizcellsxmax):
			for y in range(vizcellsymin,vizcellsymax):
				pos=[x*cellsize-camera[0]+wx//2,y*cellsize-camera[1]+wx//2]
				for i in range(8):
					if roots[x][y][i]==1 and i not in [0,1]:
						r=rootmods[i]
						if world[x][y]>0:
							wm=world[x][y]*2
						else:
							wm=0
						th=10-light[x][y]//15+wm
						#rootslv(x,y,axis,pos,r)
						ax=pos[0]+rootslv(x,y,0,pos[0],r[0][0])
						ay=pos[1]+rootslv(x,y,1,pos[1],r[0][1])
						bx=pos[0]+rootslv(x+1,y+1,0,pos[0],r[1][0])
						by=pos[1]+rootslv(x+1,y+1,1,pos[1],r[1][1])
						pg.draw.line(win,(0,0,0),(ax,ay),(bx,by),th)

	#win.blit(frog,[agent[0]-14-camera[0]+wx//2,agent[1]-40-camera[1]+wx//2])





	#pg.draw.circle(win,c,,2)
	agentcellc=[int(agent[0]//cellsize),int(agent[1]//cellsize)]#curent cell
	agentcellf=[int(agent[0]//cellsize),int(agent[1]//cellsize)]#cell below 1px
	'''
	if world[agentcellc[0]][agentcellc[1]]==0:#hitbox
		pg.draw.circle(win,cg,[agent[0]-camera[0]+wx//2,agent[1]-camera[1]+wy//2],3)#agent marker
	else:
		pg.draw.circle(win,cr,[agent[0]-camera[0]+wx//2,agent[1]-camera[1]+wy//2],3)#agent marker


	pg.draw.circle(win,cb,[camera[0]-camera[0]+wx//2,camera[1]-camera[1]+wy//2],2)#camera marker
	'''
	#win.blit(frog,(0,0))
	srf=pg.transform.scale2x(win)
	pg.transform.scale2x(srf,winW)

	pg.display.update()
	pg.display.set_caption('frog framerate '+str(framerate)+' cam '+str(camera)+' agent '+str(agent)+' falling '+str(falling)+' jumping '+str(jumping))
	mainClock.tick(framerate)
pg.quit()
sys.exit()
