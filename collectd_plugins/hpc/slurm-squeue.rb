#!/home/zimmers/opt/ruby/2.4.0/bin/ruby

# see this:
#http://docs.rightscale.com/cm/rs101/create_custom_collectd_plug-ins_for_linux.html


# The name of the collectd plugin, something like apache, memory, mysql, interface, ...
PLUGIN_NAME = 'hpc'
PLUGIN_TYPE = 'counter'

hostname    = ENV['COLLECTD_HOSTNAME'] || "localhost"
interval    = ENV['COLLECTD_INTERVAL'] || 20

def usage
  puts("#{$0} -h <host_id> [-i <sampling_interval>]")
  exit
end

# Main
begin
  # Sync stdout so that it will flush to collectd properly.
  $stdout.sync = true

  # Collection loop
  while true do
    start_run = Time.now.to_i
    next_run = start_run + interval.to_i

    # collectd data and print the values

    data = `squeue -u ${USER} -t "PD" | grep -c zimmers`.to_i
    puts("PUTVAL #{hostname}/#{PLUGIN_NAME}/#{PLUGIN_TYPE}-slurm_pending #{start_run}:#{data}")

    data = `squeue -u ${USER} -t "R" | grep -c zimmers`.to_i
    puts("PUTVAL #{hostname}/#{PLUGIN_NAME}/#{PLUGIN_TYPE}-slurm_running #{start_run}:#{data}")

    data = `squeue -u ${USER} -t "Suspended" | grep -c zimmers`.to_i
    puts("PUTVAL #{hostname}/#{PLUGIN_NAME}/#{PLUGIN_TYPE}-slurm_suspended #{start_run}:#{data}")

    data = `squeue -u ${USER} -t "CD" | grep -c zimmers`.to_i
    puts("PUTVAL #{hostname}/#{PLUGIN_NAME}/#{PLUGIN_TYPE}-slurm_completed #{start_run}:#{data}")

    data = `squeue -u ${USER} -t "F" | grep -c zimmers`.to_i
    puts("PUTVAL #{hostname}/#{PLUGIN_NAME}/#{PLUGIN_TYPE}-slurm_failed #{start_run}:#{data}")

    # sleep to make the interval
    while((time_left = (next_run - Time.now.to_i)) > 0) do
      sleep(time_left)
    end
  end
end
