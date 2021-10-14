import bpy

from os import path


join  = path.join



def bakeset():

  #  ################################
  #  RETURN SETTINGS TO BAKE AS TUPLE
  #
  #  TODO:  dis32xr  =  False                               # 32bit exr displacement mat

  calbedo  =  True                                          # all maps will bake through albedo channel
  cemit    =  False                                         # maps will be added to emission channel
  clight   =  False                                         # will lights be baked

  bkeset   =  [ calbedo, cemit, clight ]                    # bake settings

  outdir   =  "D:\\bake"                                    # out directory
  outfmt   =  "png"                                         # out image format

  bitrte   =  8                                             # out image bitrate
  resolu   =  [ 128, 128 ]                                  # output image resolution

  imgset   =  [ outdir, outfmt, bitrte, resolu ]            # export settings

  return   bkeset, imgset                                   # return to def bakechn:


def bakechn( chan, inod, pnode, matti, rgbv, prog ):

  #  ##################################################
  #  BAKE CHANNEL || WRITE COLOR
  #
  #  INPUT
  #  chan   -  input channels of materials main shadert
  #  inod   -  material node inputer descriptor
  #  pnode  -  chanel ourput to material, node pointer
  #  matti  -  target material
  #  rgbv  -   tarxget red blue green output of channel
  #

  print("prog %s" % prog)

  inme    =  ""                                              # output image name

  rd      =  float(0.0)                                      # rgb pointers
  bl      =  float(0.0)
  gn      =  float(0.0)
  ap      =  float(1.0)

  mis     =  0

  bkcfg   =  bakeset()                                       # config lists

  bkeset  =  bkcfg[0]                                        # bake options
  imgset  =  bkcfg[1]                                        # image options

  rz      =  imgset[3]                                       # resolution tuple
  odr     =  imgset[0]                                       # out directory
  ofmt    =  imgset[1]

  alb     =  bkeset[0]                                       # rum all channels through albedo
  emt     =  bkeset[1]                                       # append albedo as emission to output channel
  lgt     =  bkeset[2]                                       # direct lighting

  if( "Base" in chan ):                                      # Base Color == Albedo map  not channel
     inme =  str("%s_Albedo" % matti)                        # full out image channel name

  else:
     inme =  str("%s_%s" % (matti, chan))

  ###
  print("generating image %s" % inme )

  ofp     =   str( join( odr, inme ) )
  ofp     =   str( "%s.%s" % (ofp, ofmt) )                   # full out image path

  # bakes
  if( prog ):

     mat            =   bpy.data.materials[matti]
     ntree          =   bpy.data.materials[matti].node_tree
     image          =   bpy.data.images.new(inme, width=rz[0], height=rz[1], alpha=True, float_buffer=False, stereo3d=False, tiled=False)

     mat.use_nodes  =  True
     nodes          =  mat.node_tree.nodes
     links          =  mat.node_tree.links

     tex            =  bpy.data.images.get(inme)
     
     inode          =  mat.node_tree.nodes.new('ShaderNodeTexImage')
     inode.image    =  tex

     inode.select        =  True
     ntree.nodes.active  =  inode

     bpy.context.scene.render.engine                 =  'CYCLES'
#     bpy.context.scene.cycles.caustics_refractive    =  True
#     bpy.context.scene.cycles.caustics_reflective    =  True
#     bpy.context.scene.cycles.use_adaptive_sampling  =  True
     bpy.context.scene.render.threads                =  6

     #bpy.context.view_layer.objects.active = obj
     print("baking")

     #bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL' )
#     bpy.ops.object.bake(type='COMBINED', pass_filter={'DIRECT','INDIRECT', 'COLOR', 'EMIT'}, target='IMAGE_TEXTURES' )

     #name = "plane"
     #bpy.ops.object.select_all("EXEC_DEFAULT", action="DESELECT")
     #bpy.ops.object.select_pattern(pattern = name)
     #bpy.context.scene.objects.active = bpy.data.objects[name]
     bpy.ops.uv.lightmap_pack("EXEC_SCREEN")
     #print("Baking " + name)
     bpy.ops.object.bake("INVOKE_DEFAULT")

     #image.save_render(filepath=ofp)
     #img  =  bpy.data.images[inme]                          # new image file descriptor

     tex.alpha_mode    =  'STRAIGHT'                         # enable alpha
     tex.filepath_raw  =  ofp                                # image out fd
     tex.file_format   =  str( ofmt.upper() )                # img formage

     print("saving image")
     tex.save()                                              # save

  else:
     print("we have color on image %s" % inme)

     try:
       rd   =  rgbv[0]                                       # red out to shader via output of channel

     except:
       rd   =  float(0.0)
       mis  =  mis + 1

     try:
       bl   =  rgbv[1]                                       # blue  out  ''

     except:
       bl   =  float(0.0)
       mis  =  mis + 1

     try:
       gn   =  rgbv[2]                                       # green  ''

     except:
       gn   =  float(0.0)
       mis  =  mis + 1

     try:
       ap   =  rgbv[3]                                       # alpha is explicit

     except:
       ap   =  float(1.0)
       mis  =  mis + 1

     if( mis < 4 ):
        print("[-!]  passed a empty rgb list explicitly- BAILING")
        return

     bpy.ops.image.new(name=inme, width=rz[0], height=rz[1], color=(rd, bl, gn, ap), alpha=True, generated_type='BLANK', float=False, use_stereo_3d=False, tiled=False)

     img               =  bpy.data.images[inme]              # new image file descriptor
     img.alpha_mode    =  'STRAIGHT'                         # enable alpha
     img.filepath_raw  =  ofp                                # image out fd
     img.file_format   =  str( ofmt.upper() )                # img formage

     print("saving image")
     img.save()                                              # save


def cfgchn( chan, pnode, matti, chnls, dflts, idx ):

  #  ###########################################################
  #  FIND MATERIAL, NODE LINK DESCRIPTORS / COLOR PASSES TO BAKE
  #
  #  INPUT
  #  chan  - the channel to be baked
  #  pnode - pointer to node tree
  #  matti - material to bake from
  #  dflts - default color values for channels
  #  idx   - channel index
  #

  itx     =  False                                           # represents presence of image texture to bake
  inod    =  ""                                              # input node to channel
  rgbv    =  []                                              # provided color

  bcolor  =  pnode.inputs[chan].default_value                # an array, where base_color[0] is the Red channel
  clink   =  pnode.inputs[chan].links                        # a list of links (for inputs they are limited to 1)

  nodeloc =  pnode.location                                  # a 2d Vector that represents the position of the node in the node_editor

  ssock   =  pnode.outputs['BSDF']                           # shader pointer
  lsock   =  ssock.links                                     # shader input links pointer

  k       =  0
                                                             # match null rgb
  try:
     print(clink[0].from_node.name)                          # [!] WARNING: break test - try:except  do not remove

     itx    =  True
     ntmat  =  bpy.data.materials[matti].node_tree           # material node index
     ind    =  str( clink[0].from_node.name )                # name of node serving as input to channel
     inode  =  ntmat.nodes[ind]                              # descriptor to pointer

     poput  =  inode.outputs[0]                              # an array, where base_color[0] is the Red channel
     poput  =  str( poput ).split('"')[1]

     ilink  =  inode.outputs                                 # inpose node/channel output link

     print("[+]  Output %s connecting %s to material %s via channel %s" % (str(poput), ind, matti, chan) )


     dx  =  0

     while dx < len( inode.outputs ):                         #  traverse other output of input channel - im sure there is reason

       clr  =  inode.outputs[dx].default_value
       lk   =  inode.outputs[dx].links

       print("image output color says %s:  "  % clr)         # TODO reverse travers index of lk ilink to get descriptors of active links

       jk   =  0                                             # is active link placeholfer

       for kk in lk:

          lnk    =   str( ilink[jk] ).split('"')[1]

          print("channel out %s is active on %s" % (lnk, ind) )

          ssock  =  inode.outputs['Color']                    # shader pointer
          lsock  =  ssock.links                               # shader input links pointer

          print("ISOCKS  %s %s" % (ssock, lsock) )

          tot    =   bpy.data.materials["Material2"].node_tree.nodes["Image Texture"].outputs[0]
          dvl    =   bpy.data.materials["Material2"].node_tree.nodes["Image Texture"].outputs[0].default_value
          lkz    =   bpy.data.materials["Material2"].node_tree.nodes["Image Texture"].outputs[0].links

          print("tot %s" % str(tot) )
          print("ilink %s\n traverse chan default %s traverdse links %s" % (lnk, dvl, lkz) )

          jk     =   jk + 1

          # TODO:  iterate inputs of main shader (by index) to confirm outputs to node channel / store as arr

       dx  =  dx + 1

  except:
     print("[+] No texture for channel %s" % chan)

     dflt  =  dflts[idx]                                     # default channel value

     i     =  0                                              # rgba vertex
     k     =  0                                              # 4 defaults == matched default

     try:
        clr  =  ""
        dft  =  ""

        while i < len( bcolor ):

           clr  =  float( bcolor[i] )                        # privided rgba value by shader
           dft  =  float( dflt[i] )                          # default value index||value

           print("appending color %s" % clr)
           rgbv.append( clr )                                # appends r;g;b;a

           if( clr == dflt ):                                # check default value
              k  =  k + 1                                    # default channel colors are assumed

           else:
              i  =  i + 1                                    # next"""
     except:
       clr  =  float( bcolor )                               # privided rgba value by shader
       dft  =  float( dflt )                                 # default value index||value

       rgbv.append( clr )                                    # appends r;g;b;a

       if( clr == dflt ):                                    # check default value
          k  =  k +1

  #if( "Normal" in chan):
  #     print("[+]  setting rbgv to none/default")
       #rgbv  =  None

  # commit bake / export action

  if( itx ):                                       # image/rgb to export
     bakechn( chan, inod, pnode, matti, rgbv, "itx"  )


  elif not( itx ):
     bakechn( chan, inod, pnode, matti, rgbv, None  )

  #else:                                                        # not using this channel
  #     print("We are not using map %s" % chan)


def bakemat( chnls, matti, dflts, shade ):

  #  ########################################
  #  BAKES ALL SPECIFIED CHANNELS OF MATERIAL
  #
  #  INPUT
  #  shader   -  main principle shader
  #  chanels  -  chanels to bake
  #  matte    -  material to bake
  #
  
  # ntmat  =  bpy.data.materials[0].node_tree                 # material node indexd  
  
  ntmat  =  bpy.data.materials[matti].node_tree              # material node indexd

  pnode  =  ntmat.nodes[shade]                               # shader node index

  dist   =  pnode.distribution                               # defaults to 'GGX'

  idx    =  0                                                # channel index

  for chan in chnls:                                         # iterate desired primary channels of shader

     chan  =  str( chan )                                    # target channel

     cfgchn( chan, pnode, matti, chnls, dflts, idx )         # aquire descriptors from channel to bake

     idx   =  idx + 1
     
     break



def initcfg():

  #  ###############
  #  CONFIG SETTINGS

  matti  =  "matz"                                                                                      # material name
  shade  =  "Principled BSDF"                                                                           # main output shader

  imgrz  =  [ 1024, 1024 ]                                                                              # image resolution
  chnls  =  [ 'Base Color', 'Metallic', 'Roughness', 'Specular', 'Normal' ]                             # chanels to bakr

  dflts  =  [ [ float(0.800000011920929), float(0.800000011920929), float(0.800000011920929), float(1.0) ], float(0.000000), float(0.500000), float(0.500000), [ float(0.0), float(0.0), float(0.0) ] ]  #default values for channel

  bakemat(chnls, matti, dflts, shade)


if __name__ == "__main__":
  initcfg()
