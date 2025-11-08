#!/usr/bin/env ruby
# Copyright (C) 2003 TAKEUCHI Hitoshi <hitoshi@namaraii.com>

BEGIN { $stdout.binmode }

Encoding.default_external = 'utf-8'

$SAFE     = 1

if FileTest.symlink?( __FILE__ ) then
  org_path = File.dirname( File.expand_path( File.readlink( __FILE__ ) ) )
else
  org_path = File.dirname( File.expand_path( __FILE__ ) )
end
debug = Hash.new
debug[:org_path] = org_path.untaint
debug[:__FILE__] = __FILE__
$:.unshift( org_path.untaint, "#{org_path.untaint}/lib" )
$:.delete(".") if File.writable?(".")

debug[:LOAD_PATH] = $:
require 'pp'
PP.pp debug, STDERR


require 'cgi'
require 'hiki/config'
require 'hiki/util'

include Hiki::Util

def attach_file
  @conf = Hiki::Config.new
  set_conf(@conf)
  cgi = CGI.new

  debug = Hash.new
  params     = cgi.params
  debug[:params] = params
  require 'pp'
  PP.pp debug, STDERR
  return if params.keys.empty?

  page       = params['p'] ? params['p'][0].read : 'FrontPage'
  command = params['command'] ? params['command'][0].read : 'view'
  command = 'view' unless ['view', 'edit'].index(command)
  r = ''

  max_size = @conf.options['attach_size'] || 1048576

  if cgi.params.has_key?('attach')
    STDERR.puts "Action: attach #{cgi.params == params}"
    begin
      raise 'Invalid request.' unless params['p'] && params['attach_file']

      filename   = File.basename(params['attach_file'][0].original_filename.gsub(/\\/, '/'))
      cache_path = "#{@conf.cache_path}/attach"

      Dir.mkdir(cache_path) unless test(?e, cache_path.untaint)
      attach_path = "#{cache_path}/#{escape(page)}"
      Dir.mkdir(attach_path) unless test(?e, attach_path.untaint)

      encoded_filename = filename
      case @conf.charset
      when 'EUC-JP'
        encoded_filename = filename.to_euc
      when 'Shift_JIS'
        encoded_filename = filename.to_sjis
      end
      path = "#{attach_path}/#{escape(encoded_filename)}"
      if params['attach_file'][0].size > max_size
        raise "File size is larger than limit (#{max_size} bytes)."
      end
      unless encoded_filename.empty?
        content = params['attach_file'][0].read
        if (!@conf.options['attach.allow_script']) && (/<script\b/i =~ content)
          raise "You cannot attach a file that contains scripts."
        else
          open(path.untaint, "wb") do |f|
            f.print content
          end
          r << "FILE        = #{File.basename(path)}\n"
          r << "SIZE        = #{File.size(path)} bytes\n"
          STDERR.puts path
          STDERR.puts r
          send_updating_mail(page, 'attach', r) if @conf.mail_on_update
        end
      end
      
      STDERR.puts 'RedirectTo: ' + "#{@conf.index_url}?c=#{command}&p=#{escape(page)}"
      redirect(cgi, "#{@conf.index_url}?c=#{command}&p=#{escape(page)}")
    rescue Exception => ex
      print cgi.header( 'type' => 'text/plain' )
      puts "Debug: " + ex.message
      pp ex.backtrace
    end
  elsif cgi.params.has_key?('detach') then
    STDERR.puts "Action: detach"
    attach_path = "#{@conf.cache_path}/attach/#{escape(page)}"

    begin
      Dir.foreach(attach_path) do |file|
        next unless params["file_#{file}"]
        path = "#{attach_path}/#{file}"
        file_key = "file_#{file}"
        if FileTest.file?(path.untaint) and params.has_key?(file_key) &&  !params[file_key][0].read.empty? 
          File.unlink(path)
          r << "FILE        = #{File.basename(path)}\n"
        end
      end
      Dir.rmdir(attach_path) if Dir.entries(attach_path).size == 2
      send_updating_mail(page, 'detach', r) if @conf.mail_on_update
      redirect(cgi, "#{@conf.index_url}?c=#{command}&p=#{escape(page)}")
    rescue Exception => ex
      print cgi.header( 'type' => 'text/plain' )
      puts ex.message
      pp ex.backtrace
    end
  end
end

attach_file
