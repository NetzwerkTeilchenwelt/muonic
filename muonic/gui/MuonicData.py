"""
Provides the data and file handling for muonic
"""
import os
import datetime
import shutil

class MuonicFile(object):
    """
    Defines the basic file class for muonic. Use ''MuonicFile.muonic_file'' to access the file properties. 
    """

    def __init__(self, mfile, mode = 'r'):
        if not isinstance(mfile, str):
            raise ValueError, "Wrong file name / path"
        self.muonic_file_name = mfile
        self._mode = 'r'
        self.mode(mode)
        self.muonic_file = file(self.muonic_file_name, self._mode)
        self.datapath = os.getenv('HOME')+os.sep+'muonic_data'
    
    def muonic_file(self):
        """
        access the file properties, inherits from file
        """
        return self.muonic_file

    def muonic_file_name(self):
        """
        returns the file name
        """
        return self.muonic_file_name

    def mode(self, mode = None):
        """
        Access the file mode: if a value for the mode is given it overwrites the exisiting mode flag, else it returns the mode flag.
        """
        if mode is not None:
            mode = str(mode)            
            if mode in ['r', 'rw', 'a', 'r+', 'w+', 'a+', 'rb', 'rwb', 'ab', 'r+b', 'w+b', 'a+b']:
                self._mode = mode
            else:
                raise ValueError, "Unsupported file mode: %s" % mode
        return self._mode

    def comment_file(self, comment = ''):
        """
        Writes a comment about the measurment run start with date and time
        """
        if not self._mode in ['rw', 'a', 'w+', 'a+', 'rwb', 'ab', 'w+b', 'a+b']:
            raise IOError, "File not writeable!"
        if not isinstance(comment, str):
            raise ValueError, "Comment is not a valid string!"
        self.muonic_file.write(comment.strip())
        return True
    
    def flush(self):
        """
        Shortform of flush
        """
        self.muonic_file.flush()
        os.fsync(self.muonic_file)
        return True

    def __del__(self):
        if not self.muonic_file.closed:
            self.muonic_file.flush()
            os.fsync(self.muonic_file)
            self.muonic_file.close()
        del self.muonic_file
        del self._mode
        print "Successfully closed the file: %s" % self.muonic_file_name
        del self.muonic_file_name

class MuonicRateFile(MuonicFile):
    """
    Class which holds rate files. Contains rates in the format:

    """
    def __init__(self, filename, logger, mode = 'a'):
        self.filename = str(filename)
        self.logger = logger
        self._rate_mes_start = datetime.datetime.now()
        MuonicFile.__init__(self,self.filename, mode)

    def start_run(self, measurement = 'rate'):
        """
        Writes a comment about the measurment run start with date and time
        """
        date = datetime.now()        
        __comment_file = '# new %s measurement run from: %i-%i-%i %i-%i-%i\n' %(measurement, date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def stop_run(self):
        """
        Writes a comment about the measurment run stop with date and time
        """
        date = datetime.now()
        __comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def write(self, msg):
        """
        Replace the default write method
        """
        if msg is None:
            raise ValueError, "Missing something to write to the file."
        self.muonic_file.write(str(msg)+'\n')
        return True

    def close(self):
        """
        Closes the file and moves it to its proper place.
        """
        self.flush()
        self.muonic_file.close()
        __mtime = datetime.datetime.now() - self._rate_mes_start
        __mtime = round(__mtime.seconds/(3600.),2) + __mtime.days*86400
        self.logger.info("The rate measurement was active for %f hours" % __mtime)
        _newratefilename = self.filename.replace("HOURS",str(__mtime))
        shutil.move(self.filename,_newratefilename)
        return True


class MuonicPulseFile(MuonicFile):
    """
    Class which holds pulse files. Contains pulses in the format:
    lasttriggertime,pulses["ch0"],pulses["ch1"],pulses["ch2"],pulses["ch3"]
    """
    def __init__(self, filename, logger, mode = 'a'):
        self.filename = str(filename)
        self.logger = logger
        self._pulse_mes_start = datetime.datetime.now()
        MuonicFile.__init__(self,self.filename, mode)

    def start_run(self, measurement = 'rate'):
        """
        Writes a comment about the measurment run start with date and time
        """
        date = datetime.now()        
        __comment_file = '# new %s measurement run from: %i-%i-%i %i-%i-%i\n' %(measurement, date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def stop_run(self):
        """
        Writes a comment about the measurment run stop with date and time
        """
        date = datetime.now()
        __comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def write(self, msg):
        """
        Replace the default write method. The expected type of msg is a tuple with the content:
        (lasttriggertime,pulses["ch0"],pulses["ch1"],pulses["ch2"],pulses["ch3"])
        """
        if msg is None or not isinstance(msg, tuple):
            raise ValueError, "Missing something valid to write to the file."
        self.muonic_file.write(str(msg.__repr__())+'\n')
        return True

    def close(self):
        """
        Closes the file and moves it to its proper place.
        """
        self.flush()
        self.muonic_file.close()
        __mtime = datetime.datetime.now() - self._pulse_mes_start
        __mtime = round(__mtime.seconds/(3600.),2) + __mtime.days*86400
        self.logger.info("The rate measurement was active for %f hours" % __mtime)
        _newfilename = self.filename.replace("HOURS",str(__mtime))
        shutil.move(self.filename,_newfilename)
        return True


class MuonicVelocityFile(MuonicFile):
    """
    Class which holds velocity files. Contains dt values in ns in the format:

    """
    def __init__(self, filename, mode = 'r'):
        self.filename = filename
        # magic file renaming here
        MuonicFile.__init__(self.filename, mode)
    def close(self):
        # magic close moves here
        pass


class MuonicDecayFile(MuonicFile):
    """
    Class which holds decay measurment files. Decay dts in the format:

    """
    def __init__(self, filename, logger, mode = 'a'):
        self.filename = str(filename)
        self.logger = logger
        self._pulse_mes_start = datetime.datetime.now()
        MuonicFile.__init__(self,self.filename, mode)

    def start_run(self, measurement = 'rate'):
        """
        Writes a comment about the measurment run start with date and time
        """
        date = datetime.now()        
        __comment_file = '# new %s measurement run from: %i-%i-%i %i-%i-%i\n' %(measurement, date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def stop_run(self):
        """
        Writes a comment about the measurment run stop with date and time
        """
        date = datetime.now()
        __comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def write(self, msg):
        """
        Replace the default write method
        """
        if msg is None or len(msg) < 2:
            raise ValueError, "Missing something to write to the file."
        __msg = 'Decay ' + muondecay[1].replace(' ','_').__repr__() + ' ' + muondecay[0].__repr__()
        self.muonic_file.write(str(__msg)+'\n')
        return True

    def close(self):
        """
        Closes the file and moves it to its proper place.
        """
        self.flush()
        self.muonic_file.close()
        __mtime = datetime.datetime.now() - self._pulse_mes_start
        __mtime = round(__mtime.seconds/(3600.),2) + __mtime.days*86400
        self.logger.info("The rate measurement was active for %f hours" % __mtime)
        _newfilename = self.filename.replace("HOURS",str(__mtime))
        shutil.move(self.filename,_newfilename)
        return True


class MuonicRawFile(MuonicFile):
    """
    Class which holds raw data files. Raw data stream saved in the format:

    """
    def __init__(self, filename, logger, mode = 'a'):
        self.filename = str(filename)
        self.logger = logger
        self._pulse_mes_start = datetime.datetime.now()
        MuonicFile.__init__(self,self.filename, mode)

    def start_run(self, measurement = 'rate'):
        """
        Writes a comment about the measurment run start with date and time
        """
        date = datetime.now()        
        __comment_file = '# new %s measurement run from: %i-%i-%i %i-%i-%i\n' %(measurement, date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def stop_run(self):
        """
        Writes a comment about the measurment run stop with date and time
        """
        date = datetime.now()
        __comment_file = '# stopped run on: %i-%i-%i %i-%i-%i\n' %(date.year,date.month,date.day,date.hour,date.minute,date.second)
        self.comment_file(__comment_file)
        return True

    def write(self, msg, nostatus = False):
        """
        Replace the default write method
        """
        if msg is None:
            raise ValueError, "Missing something to write to the file."
        if nostatus:
            fields = msg.rstrip("\n").split(" ")
            if ((len(fields) == 16) and (len(fields[0]) == 8)):
                self.muonic_file.write(str(msg)+'\n')
            else:
                self.logger.debug("Not writing line '%s' to file because it does not contain trigger data" %msg)
        else:
            self.muonic_file.write(str(msg)+'\n')
        return True

    def close(self):
        """
        Closes the file and moves it to its proper place.
        """
        self.flush()
        self.muonic_file.close()
        __mtime = datetime.datetime.now() - self._pulse_mes_start
        __mtime = round(__mtime.seconds/(3600.),2) + __mtime.days*86400
        self.logger.info("The rate measurement was active for %f hours" % __mtime)
        _newfilename = self.filename.replace("HOURS",str(__mtime))
        shutil.move(self.filename,_newfilename)
        return True


class MuonicPulses(object):
    """
    Stores the pulses. pulses are appended, so 0 position is the oldest, -1 the newest
    """
    def __init__(self, triggertime, pulses):
        # pulses format: pulses_container =list containing:
        #                   --> poistion 0 containing:
        #                           --> channel[0], .....channel[n] with channel[i] containing:
        #                               --> pulse[0], ....
        # all in lists
        self._container_length = 1
        self._triggers = list()
        self._pulsesseries = list()
        self.__dummy_pulse_keys = None
        if not isinstance(pulses, list) and not isinstance(pulses, dict):
            raise ValueError, "Initializing pulses have no valid type"
        if not self.__checktime(pulses):
            raise ValueError, "Invalid pulses"
        if isinstance(pulses, dict):
            self._pulsesseries.append(pulses.values())
            self.__dummy_pulse_keys = pulses.keys()
        else:
            self._pulsesseries.append(pulses)
        if not self.__checktime(triggertime):
            raise ValueError, "Invalid _triggers"
        if isinstance(triggertime, list) or isinstance(triggertime, tuple):
            self._triggers = list(triggertime)
        else:
            self._triggers.append(triggertime)
        self._channels = len(self._pulsesseries[0])
        self.__check_length()
     
    def __checktime(self, timestamp):
        """
        Check the validity of a timestamp
        """
        if isinstance(timestamp, list) or isinstance(timestamp, tuple):
            for value in timestamp:
                if (not isinstance(value, int)) and (not isinstance(value, float)):
                    return False
        else:
            if (not isinstance(timestamp, int)) and (not isinstance(timestamp, float)):
                return False
        return True
   
    def trigger_time(self, position = -1, triggertime = None):
        """
        Returns the trigger time in the pulses or writes a new one (if given triggertime), at a position (default: latest, if None: all)
        """
        self.__check_length()
        if triggertime is None:
            if position is None:
                return self._triggers
            return self._triggers[position]
        if self.__checktime(triggertime):
            if position is None or position == -1:
                self._triggers.append(triggertime)
                self._pulsesseries.append([None]*self._channels)
            else:
                self._triggers[position] = triggertime
            self.__check_length()
            return True
        return False
    
    def pulses(self, channel = None, position = -1, pulses = None):
        """
        Returns a pulse time of a channel, or if no channel given of all channels, at a position (default: first in the list, if None: all), or writes new pulses
        """
        self.__check_length()
        if pulses is None:
            if channel is None:
                if position is None:
                    if self.__dummy_pulse_keys is None:
                        return self._pulsesseries
                    pulsesdictseries = list()
                    for pulsseries in self._pulsesseries:
                        pulsesdictseries.append(dict(zip(self.__dummy_pulse_keys,pulsseries)))
                    return pulsesdictseries
                if not self.__dummy_pulse_keys is None:
                    return dict(zip(self.__dummy_pulse_keys,self._pulsesseries[position]))
                return self._pulsesseries[position]
            if position is None:
                pulsseries = list()
                if not self.__dummy_pulse_keys is None:
                    channel = self.__dummy_pulse_keys.index(channel)
                for pulses in self._pulsesseries:
                    pulsseries.append(pulses[channel])
                return pulsseries
        if position is None:
            position = -1
        if channel is None:
            if isinstance(pulses, dict):
                if not self.__dummy_pulse_keys == pulses.keys():
                    return False
                pulses = pulses.values()
            else:
                if not self._channels == len(pulses):
                    return False
            if self.__checktime(pulses):
                if position == -1:
                    self._triggers.append(None)
                    self._pulsesseries.append(pulses)
                else:
                    self._pulsesseries[position] = pulses
                self.__check_length()
                return True
            return False
        else:
            pulsseries = list()
            if not self.__dummy_pulse_keys is None:
                channel = self.__dummy_pulse_keys.index(channel)
            if isinstance(pulses, dict):
                pulses = pulses.values()
            if not self.__checktime(pulses):
                return False
            for k in range(self._channels):
                if not k == channel:
                    pulsseries.append([])
                else:
                    pulsseries.append(pulses)
            if position == -1:
                self._triggers.append(None)
                self._pulsesseries.append(pulsseries)
            else:
                self._pulsesseries[position] = pulsseries
            self.__check_length()
            return True
        return False
    
    def __check_length(self):
        """
        Checks the container length and cuts the overhead of the container away
        """
        while len(self._pulsesseries) > self._container_length:
            del(self._pulsesseries[0])
        while len(self._triggers) > self._container_length:
            del(self._triggers[0])
        if len(self._triggers) != len(self._pulsesseries):
            raise ValueError, "Pulses container got inconsistent!"
        return True