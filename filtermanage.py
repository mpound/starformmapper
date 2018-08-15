#!/usr/bin/env python
#
# Module to manage bands (filters) and filtersets
# E.g. convert magnitude to flux and vice versa for various wavebands.
#
#
import warnings
import numpy as np
#import enum
from astropy import units as u
from astropy.units.quantity import Quantity
import quantityhelpers as qh
import math


"""Telescope names"""
SDSS     = "SDSS"
SLOAN    = "SDSS"
SPITZER  = "Spitzer"
GAIA     = "GAIA"
GAIA2     = "GAIA2"
GAIA2r     = "GAIA2r"
HERSCHEL = "Herschel"
TWOMASS  = "2MASS"
WISE     = "WISE"
GENERIC  = "Generic" # This is a guess as to which Bessel filter set Robitaille used.  They are slightly different for different telescopes


"""Photometric band names. Where common, use same names as SedFitter code (Robitaille)"""
# @Todo Replace all these with Enums?
#SDSS = Enum(SLOAN, "u g r i z")
# Sloan Digital Sky Survey
SDSS_u = "SDSS_u"
SDSS_g = "SDSS_g"
SDSS_r = "SDSS_r"
SDSS_i = "SDSS_i"
SDSS_z = "SDSS_z"
# Bessel UVBRI
BESSELL_U  = "BU"
BESSELL_B  = "BB"
BESSELL_V  = "BV"
BESSELL_R  = "BR"
BESSELL_I  = "BI"
# GAIA
GAIA_G2  = "GAIA_G2"
GAIA_B2  = "GAIA_BP2"
GAIA_R2  = "GAIA_RP2"
GAIA_G2r  = "GAIA_G2r"
GAIA_B2r  = "GAIA_BP2r"
GAIA_R2r  = "GAIA_RP2r"
# 2MASS
TWOMASS_J = "2J"
TWOMASS_H = "2H"
TWOMASS_K = "2K"
#DENIS_I   = "Id"
#USNO_B    = "Bu"
#USNO_R    = "Ru"
# Spitzer
IRAC1 = "I1"
IRAC2 = "I2"
IRAC3 = "I3"
IRAC4 = "I4"
MIPS1 = "M1"
MIPS2 = "M2"
MIPS3 = "M3"
# Herschel
PACS_B = "PACS1"
PACS_G = "PACS2"
PACS_R = "PACS3"
# WISE
WISE1  = "WISE1"
WISE2  = "WISE2"
WISE3  = "WISE3"
WISE4  = "WISE4"

# can be used to reverse lookup the telescope
_valid_bands = {
    # Sloan
    SDSS_u:SLOAN,
    SDSS_g:SLOAN,
    SDSS_r:SLOAN,
    SDSS_i:SLOAN,
    SDSS_z:SLOAN,
    # Bessel UVBRI
    BESSELL_U:GENERIC,
    BESSELL_B:GENERIC,
    BESSELL_V:GENERIC,
    BESSELL_R:GENERIC,
    BESSELL_I:GENERIC,
    GAIA_G2:GAIA,
    GAIA_B2:GAIA,
    GAIA_R2:GAIA,
    GAIA_G2r:GAIA,
    GAIA_B2r:GAIA,
    GAIA_R2r:GAIA,
    # 2MASS
    TWOMASS_J:TWOMASS,
    TWOMASS_H:TWOMASS,
    TWOMASS_K:TWOMASS,
    #DENIS_I,
    #USNO_B,
    #USNO_R,
    # Spitzer
    IRAC1:SPITZER,
    IRAC2:SPITZER,
    IRAC3:SPITZER,
    IRAC4:SPITZER,
    MIPS1:SPITZER,
    MIPS2:SPITZER,
    MIPS3:SPITZER,
    # Herschel
    PACS_B:HERSCHEL,
    PACS_G:HERSCHEL,
    PACS_R:HERSCHEL,
    # WISE
    WISE1:WISE,
    WISE2:WISE,
    WISE3:WISE,
    WISE4:WISE
}

def validbands(): 
    return _valid_bands.keys()


class Band():
    """
    Class to hold information about a photometric band (filter)

    Parameters:
       name (str): canonical name of the band, e.g. 'u' or SDSS_u
       wavelength (astropy.units.quantity.Quantity): mean wavelength of the band
       bandwidth (astropy.units.quantity.Quantity):  effective bandwidth of the band, in units of (wave)length
       zeropoint (astropy.units.quantity.Quantity):  equivalent flux density of zero magnitude
    """
    def __init__(self,name,wavelength,bandwidth,zeropoint):
       # canonical name
       self._name = name
       # mean wavelength
       if not qh.isQuantity(wavelength):
          raise Exception("Wavelength must be an astropy Quantity")
       if not qh.isQuantity(bandwidth):
          raise Exception("Wavelength must be an astropy Quantity")
       if not qh.isQuantity(zeropoint):
          raise Exception("Wavelength must be an astropy Quantity")

       # Check that units of inputs are correct dimensions.
       # This is done by trying to convert them to angstrom, jansky
       try: 
           wavelength.to(u.angstrom)
       except Exception:
           raise Exception("Wavelength must have units of wavelength.")

       try: 
           bandwidth.to(u.angstrom)
       except Exception:
           raise Exception("Bandwidth must have units of wavelength.")

       try: 
           zeropoint.to(u.jansky)
       except Exception:
           raise Exception("Zeropoint must have units of flux density.")

       self._wavelength = wavelength
       # effective wavelength
       self._bandwidth  = bandwidth
       # flux zeropoint
       self._zeropoint  = zeropoint

    """Returns band canonical name"""
    def name(self): return self._name

    """Returns mean wavelength (astropy Quantity)"""
    def wave(self): return self._wavelength

    """Returns effective bandwidth (astropy Quantity)"""
    def bw(self):   return self._bandwidth

    """Returns zero point flux density (astropy Quantity)"""
    def zp(self):   return self._zeropoint

class FilterSet():
    """
    Class to hold information about a full set of filters, e.g. Sloan u,g,r,i,z
    This class acts as a dictionary, keyed by the stored Band names (lowercase).
    
    Parameters:
         name (str): name of the filter set
         bands (obj): Band or list of Bands to add to the set, optional. See also addBands()

    Bands will be stored in an internal dictionary indexed by the lowercase bandname.
    """

    def __init__(self,name,bands=None):
       self._name  = name  
       self._bands = dict()
       if bands != None: self.addBands(bands)

    # add one or more Band objects
    # Parameters:
    #   bands:  single Band or list of Bands
    def addBands(self,bands):
       if type(bands) != list:
          bands=list(bands)
       for band in bands:
            self._bands[band._name.lower()] = band

    # make this class act like a dictionary keyed by band name
    """Returns Band object associated with band name (case insensitive)"""
    def __getitem__(self,bandname):
       return self._bands[bandname.lower()]

    # make this class act like a dictionary keyed by band name
    """Set Band object associated with band name (case insensitive)"""
    def __setitem__(self,bandname,band):
       if type(band) != Band:
          raise Exception("Assignment value must be a Band object")
       self._bands[bandname.lower()] = band
 
######################################################################################
# Mean wavelengths and effective bandwidths in angstrom & Zero Points 
# in Jansky of various filter sets,  taken from VOSA website.  
# http://svo2.cab.inta-csic.es/theory/fps/

# Create any new FilterSets here.

# SDSS
sloan    = [Band(SDSS_u, 3561.8*u.angstrom,  558.4*u.angstrom, 1568.5*u.jansky),
            Band(SDSS_g, 4718.9*u.angstrom, 1158.4*u.angstrom, 3965.9*u.jansky),
            Band(SDSS_r, 6185.2*u.angstrom, 1111.2*u.angstrom, 3162.0*u.jansky),
            Band(SDSS_i, 7499.7*u.angstrom, 1044.6*u.angstrom, 2602.0*u.jansky),
            Band(SDSS_z, 8961.5*u.angstrom, 1124.6*u.angstrom, 2244.7*u.jansky)
           ]

# Generic
bessel  = [Band(BESSELL_U, 3605.1*u.angstrom,  640.4*u.angstrom, 1803.1*u.jansky),
           Band(BESSELL_B, 4400.0*u.angstrom,  900.0*u.angstrom, 4000.0*u.jansky),
           Band(BESSELL_V, 5312.1*u.angstrom,  893.1*u.angstrom, 3579.8*u.jansky),
           Band(BESSELL_R, 6575.9*u.angstrom, 1591.0*u.angstrom, 2971.4*u.jansky),
           Band(BESSELL_I, 8059.9*u.angstrom, 1495.1*u.angstrom, 2405.3*u.jansky)
          ]
# Gaia 2nd release  (GAIA2) values
gaia2   = [Band(GAIA_B2, 5279.9*u.angstrom, 2347.4*u.angstrom, 3534.7*u.jansky),
           Band(GAIA_G2, 6742.5*u.angstrom, 4183.0*u.angstrom, 3296.2*u.jansky),
           Band(GAIA_R2, 7883.7*u.angstrom, 2756.8*u.angstrom, 2620.3*u.jansky)
          ]

# Gaia 2nd Release revised (GAIA2r) values
gaia2r   = [Band(GAIA_B2r, 5278.6*u.angstrom, 2279.4*u.angstrom, 3393.3*u.jansky),
           Band(GAIA_G2r, 6773.7*u.angstrom, 4358.4*u.angstrom, 2835.1*u.jansky),
           Band(GAIA_R2r, 7919.1*u.angstrom, 2943.7*u.angstrom, 2485.1*u.jansky)
          ]
# 2MASS
twomass = [Band(TWOMASS_J, 12350.0*u.angstrom, 1624.1*u.angstrom, 1594.0*u.jansky), 
           Band(TWOMASS_H, 16620.0*u.angstrom, 2509.4*u.angstrom, 1024.0*u.jansky), 
           Band(TWOMASS_K, 21590.0*u.angstrom, 2618.9*u.angstrom,  666.8*u.jansky)
          ]

# Spitzer Space Telescope
spitzer = [Band(IRAC1 , 35572.6*u.angstrom ,    6836.2*u.angstrom, 277.2*u.jansky), 
           Band(IRAC2 , 45049.3*u.angstrom ,    8649.9*u.angstrom, 179.0*u.jansky), 
           Band(IRAC3 , 57385.7*u.angstrom ,   12561.2*u.angstrom, 113.8*u.jansky), 
           Band(IRAC4 , 79273.7*u.angstrom ,   25288.5*u.angstrom,  62.0*u.jansky), 
           Band(MIPS1 , 238433.1*u.angstrom ,  52963.2*u.angstrom,   7.1*u.jansky), 
           Band(MIPS2  , 725555.3*u.angstrom , 213015.3*u.angstrom,   0.8*u.jansky), 
           Band(MIPS3 ,1569627.1*u.angstrom , 357530.2*u.angstrom,   0.2*u.jansky)
          ]

# Herschel Space Telescope
herschel = [Band(PACS_B,  719334.2*u.angstrom, 214148.9*u.angstrom, 0.8*u.jansky),
            Band(PACS_G, 1026174.6*u.angstrom, 312860.0*u.angstrom, 0.4*u.jansky),
            Band(PACS_R, 1671355.3*u.angstrom, 697595.3*u.angstrom, 0.1*u.jansky)
           ]

# Widefield Infrared Space Explorer (WISE)
wise     = [Band(WISE1,33526.0*u.angstrom, 6626.4*u.angstrom,  309.5*u.jansky),
            Band(WISE2,46028.0*u.angstrom, 10422.7*u.angstrom, 171.8*u.jansky),
            Band(WISE3,115608.0*u.angstrom, 55055.7*u.angstrom, 31.7*u.jansky),
            Band(WISE4,220883.0*u.angstrom, 41016.8*u.angstrom,  8.4*u.jansky)
           ]

# add any new FilterSets to this list
all_filtersets = [ sloan, gaia2, bessel, twomass, spitzer, herschel, wise ]
all_names      = [ SLOAN, GAIA, GENERIC, TWOMASS, SPITZER, HERSCHEL, WISE ]


######################################################################################

class FilterSetManager():

    """Class to manage operations associated with sets of filters (Bands)"""
    # Add all filtersets 
    def __init__(self):
       self._filtersets = dict()
       #print(self._filtersets)
       self._fslist = list()
       for f,n in zip(all_filtersets,all_names):
           fs = FilterSet(n)
           fs.addBands(f)
           self._fslist.append(fs)
           #print("added %s"%(n))
 
       self.addFilterSets(self._fslist)

    """
    Add a set of filters.
    Parameters;
      filtersets - a list of FilterSet objects or single FilterSet
    """
    def addFilterSets(self,filtersets):
       if type(filtersets) != list:
            filtersets=list(filtersets)
       for f in filtersets:
            self._filtersets[f._name.lower()] = f
            #print("added %s"%(f._name.lower()))
 

    def __getitem__(self,name):
       return self._filtersets[name.lower()]

    """Return all stored FilterSet names"""
    def filtersetnames(self):
       return self._filtersets.keys()

    """Return all Band names of a given FilterSet"""
    def bandnames(self,filterset):
       return self._filtersets[filterset].keys()

    """Return all the zero point of a given Band and FilterSet, as astropy Quantity"""
    def zeropoint(self,filterset,band):
       return self._filtersets[filterset][band].zp()

    """Return all the mean wavelength of a given Band and FilterSet, as astropy Quantity"""
    def wavelength(self,filterset,band):
       return self._filtersets[filterset][band].wave()

    """Return all the effective bandwidth of a given Band and FilterSet, as astropy Quantity"""
    def bandwidth(self,filterset,band):
       return self._filtersets[filterset][band].bw()

    # Return given (milli)jansky
    # Example: magtoflux("sloan","SDSS_u",10)  returns 156.85 mJy 
    # @returns astropy Quantity with units u.mJy or u.Jy
    def magtoflux(self,telescope,band,magnitude,mjy=True):
       """Return the flux density in Jansky or milliJansky of a source as an astropy Quantity, 
          given the source magnitude.
          Parameters:
             telescope - string or (string constant) telescope name, e.g.
                         SLOAN, 'gaia', '2MASS', 'Spitzer', HERSCHEL, WISE 
             band      - wave band name of telescope e.g., 'u' or SDSS_u for Sloan, IRAC1 or 'I1' for spitzer
             magnitude - magnitude of source, as scalar or astropy magnitude Quantity
             mjy       - boolean to return flux in mJy. True returns mJy, False returns Jy. Default:True
       """
       zpjy = self._filtersets[telescope.lower()][band].zp().to(u.Jy)
       #print("TBM: %s %s %s %s"%(telescope,band,magnitude,zpjy))
       if qh.isMagnitude(magnitude):
           value = zpjy*10.0**(magnitude.value/-2.5)
       else:
           value = zpjy*10.0**(magnitude/-2.5)
       if mjy == True:
           return value.to(u.mJy)
       else:
           return value.to(Jy)

    # Return magnitude given jansky
    # Example: fluxtomag("sloan","SDSS_u",156.85)  returns 10 mag
    # @returns astropy Quantity with units u.Magnitude)
    def fluxtomag(self,telescope,band,flux,mjy=True):
       """Return the magnitude given flux in Jansky as magnitude astropy Quantity.
          Parameters:
             telescope - string telescope name, one of
                         sloan, gaia, 2MASS, Spitzer, Herschel, Wise - case insensitive
             band      - wave band name of telescope e.g., 'u' for sloan, 'I1' for spitzer
             flux      - flux density of source, scalar in Jy or mJy, or Astropy Quantity with units of flux density
             mjy       - boolean, True if flux was given in mJy False if Jy. Ignored if flux is given as Quantity
       """
       zpjy = self._filtersets[telescope.lower()][band].zp().to(u.Jy)
       if qh.isQuantity(flux):
           fval = flux.to(u.Jy).value
       else:
           if mjy==True: fval = flux / 1000.0
           else:         fval = flux
       return u.Magnitude(-2.5*np.log10(fval/zpjy.value))

class Photometry():
#@todo deal with masked values
    "A single photometric point"
    def __init__(self,bandname,flux,error,validity,unit=None):
       if bandname not in _valid_bands:
          warnings.warn("Unrecognized band name %s. Will not be able to convert between flux density and magnitude." % bandname)
       self._bandname = bandname

       if qh.isFluxDensity(flux) or qh.isMagnitude(flux):
           self._flux = flux
       else:
           if unit == None:
               raise Exception("flux or unit must be a Magnitude or Flux Density Quantity")
           else:
               self._flux = flux*unit
       if qh.isFluxDensity(error) or qh.isMagnitude(error):
           self._error = error 
       else:
           if unit == None:
               raise Exception("error must be a Magnitude or Flux Density Quantity")
           else:
               self._error = error*unit

       if not ((qh.isFluxDensity(self._flux) and qh.isFluxDensity(self._error)) or (qh.isMagnitude(self._flux) and qh.isMagnitude(self._error))):
               raise Exception("flux and error must be a Magnitude or Flux Density Quantity and have equivalent units")

       self._validity = validity
       self._fsm      = FilterSetManager()

    @property
    def band(self):
        return self._bandname

    @property
    def wavelength(self):
        tel = _valid_bands[self._bandname].lower()
        return self._fsm.wavelength(tel,self._bandname)

    @property
    def flux(self):
        """return flux as flux density quantity"""
        if qh.isMagnitude(self._flux):
            tel = _valid_bands[self._bandname].lower()
            return self._fsm.magtoflux(tel,self._bandname,self._flux) 
        else:
            return self._flux

    def mjy(self):
        return self.flux.to(u.mJy).value

    @property
    def magnitude(self):
        """return flux as magnitude quantity"""
        if qh.isFluxDensity(self._flux):
            tel = _valid_bands[self._bandname].lower()
            return self._fsm.fluxtomag(tel,self._bandname,self._flux) 
        else:
            return self._flux

    @property
    def error(self):
        """return error as flux density quantity"""
        if qh.isMagnitude(self._error):
            tel = _valid_bands[self._bandname].lower()
            return self._fsm.magtoflux(tel,self._bandname,self._error) 
        else:
            return self._error

    def errormag(self):
        """return error as magnitude quantity"""
        if qh.isFluxDensity(self._error):
            NtoS = self._error/self._flux
            magerror = 2.5*math.log10(1.0+NtoS)
            return u.Magnitude(magerror)
        else:
            return self._error

    def errormjy(self):
        """return error in millijanskies as a scalar"""
        if qh.isMagnitude(self._error):
            NtoS = 10.0**(self._error.value/2.5)-1.0
            tel = _valid_bands[self._bandname].lower()
            fluxmjy=  self._fsm.magtoflux(tel,self._bandname,self._flux)
            errormjy = fluxmjy * NtoS
#            print("tel %s, band %s, error %s, NtoS %s fluxmjy %s errormjy %s"%(tel,self._bandname,self._error, NtoS,fluxmjy,errormjy))
            return errormjy.to(u.mJy).value 
        else:
            return self._error.to(u.mJy).value

    @property
    def validity(self):
        return self._validity
    
    def setvalidity(self,validity):
        self._validity = validity

    @property
    def units(self):
        return self._flux.unit


#### EXAMPLE USAGE ####
if __name__ == "__main__":

       """Example usage"""
       fsm = FilterSetManager()
       print("Filter sets imported:%s"%fsm.filtersetnames())

       f = fsm.magtoflux(SLOAN,SDSS_u,10)
       # note return value is Quantity
       print(f)
       print(f.to(u.Jy))
       print(f.to(u.mJy))

       m = fsm.fluxtomag(SLOAN,SDSS_u,156.85,mjy=True)
       # magnitude Quantity 
       print("Should be 10:",m) 

       # example using Quantity instead of scalar value input
       q = 1000*u.mJy
       m = fsm.fluxtomag(SPITZER,MIPS1,q)
       print(m)
       f = fsm.magtoflux(SLOAN,SDSS_u,0.0214)
       print(f)
       #SDSS = enum.Enum(SLOAN, "u g r i z")
       #print(SDSS.u.value)
       #print(SDSS.u.name)

