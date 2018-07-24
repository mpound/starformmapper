#!/usr/bin/env python
#
# Module to manage bands (filters) and filtersets
# E.g. convert magnitude to flux and vice versa for various wavebands.
#
# Additional wavebands can be added easily.
# MWP - Tue Jul 24 13:39:14 EDT 2018
#
import numpy as np
from astropy import units as u

class Band():
    """
    Class to hold information about a band (filter)

    Parameters:
       name (str): name of the band, e.g. 'u'
       wavelength (astropy.units.quantity.Quantity): mean wavelength of the band
       bandwidth (astropy.units.quantity.Quantity):  effective bandwidth of the band, in units of (wave)length
       zeropoint (astropy.units.quantity.Quantity):  equivalent flux density of zero magnitude
    """
    def __init__(self,name,wavelength,bandwidth,zeropoint):
       # canonical name
       self._name = name
       # mean wavelength
       if type(wavelength) != u.quantity.Quantity:
          raise Exception("Wavelength must be an astropy Quantity")
       if type(bandwidth) != u.quantity.Quantity:
          raise Exception("Wavelength must be an astropy Quantity")
       if type(zeropoint) != u.quantity.Quantity:
          raise Exception("Wavelength must be an astropy Quantity")

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

    """Returns band name"""
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
sloan    = [Band('u', 3561.8*u.angstrom,  558.4*u.angstrom, 1568.5*u.jansky),
            Band('g', 4718.9*u.angstrom, 1158.4*u.angstrom, 3965.9*u.jansky),
            Band('r', 6185.2*u.angstrom, 1111.2*u.angstrom, 3162.0*u.jansky),
            Band('i', 7499.7*u.angstrom, 1044.6*u.angstrom, 2602.0*u.jansky),
            Band('z', 8961.5*u.angstrom, 1124.6*u.angstrom, 2244.7*u.jansky)
           ]

# Gaia 2nd Release (GAIA2r) values
gaia    = [Band('BP', 5278.6*u.angstrom, 2279.4*u.angstrom, 3393.3*u.jansky),
           Band( 'G', 6773.7*u.angstrom, 4358.4*u.angstrom, 2835.1*u.jansky),
           Band('RP', 7919.1*u.angstrom, 2943.7*u.angstrom, 2485.1*u.jansky)
          ]
# 2MASS
twomass = [Band('J', 12350.0*u.angstrom, 1624.1*u.angstrom, 1594.0*u.jansky), 
           Band('H', 16620.0*u.angstrom, 2509.4*u.angstrom, 1024.0*u.jansky), 
           Band('K', 21590.0*u.angstrom, 2618.9*u.angstrom,  666.8*u.jansky)
          ]

# Spitzer Space Telescope
spitzer = [Band('I1'  ,  35572.6*u.angstrom ,    6836.2*u.angstrom, 277.2*u.jansky), 
           Band('I2'  ,  45049.3*u.angstrom ,    8649.9*u.angstrom, 179.0*u.jansky), 
           Band('I3'  ,  57385.7*u.angstrom ,   12561.2*u.angstrom, 113.8*u.jansky), 
           Band('I4'  ,  79273.7*u.angstrom ,   25288.5*u.angstrom,  62.0*u.jansky), 
           Band('M24' , 238433.1*u.angstrom ,   52963.2*u.angstrom,   7.1*u.jansky), 
           Band('M70' , 725555.3*u.angstrom ,  213015.3*u.angstrom,   0.8*u.jansky), 
           Band('M160',1569627.1*u.angstrom ,  357530.2*u.angstrom,   0.2*u.jansky)
          ]

# Herschel Space Telescope
herschel = [Band('PACSB',  719334.2*u.angstrom, 214148.9*u.angstrom, 0.8*u.jansky),
            Band('PACSG', 1026174.6*u.angstrom, 312860.0*u.angstrom, 0.4*u.jansky),
            Band('PACSR', 1671355.3*u.angstrom, 697595.3*u.angstrom, 0.1*u.jansky)
           ]

# Widefield Infrared Space Explorer (WISE)
wise     = [Band('W1',33526.0*u.angstrom, 6626.4*u.angstrom,  309.5*u.jansky),
            Band('W2',46028.0*u.angstrom, 10422.7*u.angstrom, 171.8*u.jansky),
            Band('W3',115608.0*u.angstrom, 55055.7*u.angstrom, 31.7*u.jansky),
            Band('W4',220883.0*u.angstrom, 41016.8*u.angstrom,  8.4*u.jansky)
           ]

# add any new FilterSets to this list
all_filtersets = [ sloan, gaia, twomass, spitzer, herschel, wise ]
all_names      = [ "sloan", "gaia", "twomass", "spitzer", "herschel", "wise" ]
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
    # Example: magtoflux("sloan","u",10)  returns 156.85 mJy 
    # @returns astropy Quantity with units u.mJy or u.Jy
    def magtoflux(self,telescope,band,magnitude,mjy=True):
       """Return the flux density in Jansky or milliJansky of a source as an astropy Quantity, 
          given the source magnitude.
          Parameters:
             telescope - string telescope name, one of
                         sloan, gaia, 2MASS, Spitzer, Herschel - case insensitive
             band      - wave band of telescope e.g., 'u' for sloan, 'I1' for spitzer
             magnitude - magnitude of source
             mjy       - boolean to return flux in mJy. True returns mJy, False returns Jy. Default:True
       """
       zpjy = self._filtersets[telescope][band].zp().to(u.Jy)
       value = zpjy*10.0**(magnitude/-2.5)
       if mjy == True:
           return value.to(u.mJy)
       else:
           return value.to(Jy)

    # Return magnitude given jansky
    # Example: fluxtomag("sloan","u",156.85)  returns 10 mag
    # @returns astropy Quantity with units u.Magnitude)
    def fluxtomag(self,telescope,band,flux,mjy=True):
       """Return the magnitude given flux in Jansky as magnitude astropy Quantity.
          Parameters:
             telescope - string telescope name, one of
                         sloan, gaia, 2MASS, Spitzer, Herschel - case insensitive
             band      - wave band of telescope e.g., 'u' for sloan, 'I1' for spitzer
             flux      - flux density of source in Jy or mJy
             mjy       - boolean, True if flux was given in mJy False if Jy
       """
       zpjy = self._filtersets[telescope][band].zp().to(u.Jy)
       if mjy==True: flux /= 1000.0
       return u.Magnitude(-2.5*np.log10(flux/zpjy.value))


if __name__ == "__main__":

       """Example usage"""
       fo = FilterSetManager()
       f = fo.magtoflux("sloan","u",10)
       print(f)
       print(f.to(u.Jy))
       print(f.to(u.mJy))
       m = fo.fluxtomag("sloan","u",156.85,mjy=True)
       print(m)