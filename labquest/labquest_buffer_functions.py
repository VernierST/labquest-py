from queue import Queue

from labquest import config


class lq_buffer:
    """ Create a buffer for the analog and digital channels of up to two labquest devices.
    The lq_buffer class uses queue to store excess data during data collection. For faster
    single-pt sampling, a call to read() may return a packet of data from the labquest. The most 
    recent data pt will be returned, the rest stored in this buffer. During the next call to read(), 
    a single data point from this buffer will be returned, rather than from the labquest. This will 
    continue until the buffer is empty, at which point the read() will again pull data from the labquest. 
	"""

    ch1_0 = Queue(maxsize=1)
    ch2_0 = Queue(maxsize=1)
    ch3_0 = Queue(maxsize=1)
    dig1_0 = Queue(maxsize=1)
    dig2_0 = Queue(maxsize=1)

    ch1_1 = Queue(maxsize=1)
    ch2_1 = Queue(maxsize=1)
    ch3_1 = Queue(maxsize=1)
    dig1_1 = Queue(maxsize=1)
    dig2_1 = Queue(maxsize=1)

    def __init__(self):
        pass

    def buffer_init(self):
        """ Initialize the buffer by setting queue(maxsize) = 0. This
        sets the upperbound limit on the number of items that can be placed in the queue.  
        When maxsize is less than or equal to zero, the queue size is infinite.
        """

        device_index = 0
        while device_index < len(config.hDevice):
            if device_index == 0:
                # all enabled channels. [[1,2,3,5,6],[1,2]]
                for ch in config.enabled_all_channels[device_index]:
                    config.logger.debug("buffer init ch" +str(ch))
                    if ch == 1:
                        lq_buffer.ch1_0 = Queue(maxsize=0)
                    if ch == 2:
                        lq_buffer.ch2_0 = Queue(maxsize=0)
                    if ch == 3:
                        lq_buffer.ch3_0 = Queue(maxsize=0)
                    if ch == 5:
                        lq_buffer.dig1_0 = Queue(maxsize=0)
                    if ch == 6:
                        lq_buffer.dig2_0 = Queue(maxsize=0)

            if device_index == 1:
                # all enabled channels. [[1,2,3,5,6],[1,2]]
                for ch in config.enabled_all_channels[device_index]:
                    config.logger.debug("buffer init ch" +str(ch))
                    if ch == 1:
                        lq_buffer.ch1_1 = Queue(maxsize=0)
                    if ch == 2:
                        lq_buffer.ch2_1 = Queue(maxsize=0)
                    if ch == 3:
                        lq_buffer.ch3_1 = Queue(maxsize=0)
                    if ch == 5:
                        lq_buffer.dig1_1 = Queue(maxsize=0)
                    if ch == 6:
                        lq_buffer.dig2_1 = Queue(maxsize=0)

            device_index += 1

    def buffer_is_empty(self, device_index, ch):
        """ Returns True if the buffer (the queue) for a specific channel is empty.
        """

        if device_index == 0:
            if ch == 1:
                is_empty = lq_buffer.ch1_0.empty()
            if ch == 2:
                is_empty = lq_buffer.ch2_0.empty()
            if ch == 3:
                is_empty = lq_buffer.ch3_0.empty()
            if ch == 5:
                is_empty = lq_buffer.dig1_0.empty()
            if ch == 6:
                is_empty = lq_buffer.dig2_0.empty()

        if device_index == 1:
            if ch == 1:
                is_empty = lq_buffer.ch1_1.empty()
            if ch == 2:
                is_empty = lq_buffer.ch2_1.empty()
            if ch == 3:
                is_empty = lq_buffer.ch3_1.empty()
            if ch == 5:
                is_empty = lq_buffer.dig1_1.empty()
            if ch == 6:
                is_empty = lq_buffer.dig2_1.empty()
                        
        config.logger.debug("buffer 'empty' ch" +str(ch) +": " +str(is_empty))
        return is_empty

    def buffer_put(self, device_index, ch, new_data):
        """ Add a list of data to the buffer for a specified channel
        """

        if device_index == 0:
            config.logger.debug("buffer 'put' ch" +str(ch) +": " +str(new_data))
            if ch == 1:
                for data in new_data:
                    lq_buffer.ch1_0.put(data)
            if ch == 2:
                for data in new_data:
                    lq_buffer.ch2_0.put(data)
            if ch == 3:
                for data in new_data:
                    lq_buffer.ch3_0.put(data)
            if ch == 5:
                for data in new_data:
                    lq_buffer.dig1_0.put(data)
            if ch == 6:
                for data in new_data:
                    lq_buffer.dig2_0.put(data)

        if device_index == 1:
            config.logger.debug("buffer 'put' ch" +str(ch) +": " +str(new_data))
            if ch == 1:
                for data in new_data:
                    lq_buffer.ch1_1.put(data)
            if ch == 2:
                for data in new_data:
                    lq_buffer.ch2_1.put(data)
            if ch == 3:
                for data in new_data:
                    lq_buffer.ch3_1.put(data)
            if ch == 5:
                for data in new_data:
                    lq_buffer.dig1_1.put(data)
            if ch == 6:
                for data in new_data:
                    lq_buffer.dig2_1.put(data)

       
    def buffer_get(self, device_index, ch):
        """ Pull a single data point from the buffer of a specified channel.
        """

        measurement = None

        if device_index == 0:
            if ch == 1:
                if lq_buffer.ch1_0.empty() == False:
                    measurement = lq_buffer.ch1_0.get()
            if ch == 2:
                if lq_buffer.ch2_0.empty() == False:
                    measurement = lq_buffer.ch2_0.get()
            if ch == 3:
                if lq_buffer.ch3_0.empty() == False:
                    measurement = lq_buffer.ch3_0.get()
            if ch == 5:
                if lq_buffer.dig1_0.empty() == False:
                    measurement = lq_buffer.dig1_0.get()
            if ch == 6:
                if lq_buffer.dig2_0.empty() == False:
                    measurement = lq_buffer.dig2_0.get()

        if device_index == 1:
            if ch == 1:
                if lq_buffer.ch1_1.empty() == False:
                    measurement = lq_buffer.ch1_1.get()
            if ch == 2:
                if lq_buffer.ch2_1.empty() == False:
                    measurement = lq_buffer.ch2_1.get()
            if ch == 3:
                if lq_buffer.ch3_1.empty() == False:
                    measurement = lq_buffer.ch3_1.get()
            if ch == 5:
                if lq_buffer.dig1_1.empty() == False:
                    measurement = lq_buffer.dig1_1.get()
            if ch == 6:
                if lq_buffer.dig2_1.empty() == False:
                    measurement = lq_buffer.dig2_1.get()
            
        config.logger.debug("buffer 'get' ch" +str(ch) +": " +str(measurement))
        return measurement


    def buffer_clear(self):
        """ Uninit the buffer by clearing queue
        """
        config.logger.debug("buffer clear")
        with lq_buffer.ch1_0.mutex:
            lq_buffer.ch1_0.queue.clear()
        with lq_buffer.ch2_0.mutex:
            lq_buffer.ch2_0.queue.clear()
        with lq_buffer.ch3_0.mutex:
            lq_buffer.ch3_0.queue.clear()
        with lq_buffer.dig1_0.mutex:
            lq_buffer.dig1_0.queue.clear()
        with lq_buffer.dig2_0.mutex:
            lq_buffer.dig2_0.queue.clear()

        with lq_buffer.ch1_1.mutex:
            lq_buffer.ch1_1.queue.clear()
        with lq_buffer.ch2_1.mutex:
            lq_buffer.ch2_1.queue.clear()
        with lq_buffer.ch3_1.mutex:
            lq_buffer.ch3_1.queue.clear()
        with lq_buffer.dig1_1.mutex:
            lq_buffer.dig1_1.queue.clear()
        with lq_buffer.dig2_1.mutex:
            lq_buffer.dig2_1.queue.clear()