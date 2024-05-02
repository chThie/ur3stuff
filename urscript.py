"""
"Pythonified" URScript to be able to run, extend and validate the script
for URScript see mqtt-ur3-bridge-main-with-queue.txt
"""

end = None
get_list_length = len
to_num = float

targetPose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
targetJoints = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
vel = 0.0
acc = 0.0
blend = 0.0
time = 0.0

# cmd_queue = ["movePos", "movejPose", "movejJoints", "movejPose"]
# val_queue = ["3", "blend", "time", "blend,time"]
# arg_queue = [[], [0.1, 0.2, -0.1, 0.1, 0.2, -0.1, 1, 0.5], [-0.1, 0.1, 0.1, 0.3, -0.2, 0.2, 1, 0.5],
#              [0.1, 0.2, -0.1, 0.1, 0.2, -0.1, 1, 0.5]]

cmd_queue = []
val_queue = []
arg_queue = []
q_length = 0


def set_entry(q, i, v):
    """
    Set queue value v on index i (q[i]=v).

    necessary because we can't assign to a value in the q[i]=v way if i is not a counter in a while loop
    at least on the teach pendant (I don't know why URScript is ...like that)
    """
    r = 0
    while True:
        if r == i:
            # q[i] = v
            q.append(v)
            return
        r = r + 1
    end
end


def thread1():
    global q_length, targetPose, targetJoints, vel, acc, blend, time, cmd_queue, val_queue, arg_queue
    while True:
        'extract next command and args from queues'
        next_cmd = ""
        next_args = []
        q_length = get_list_length(cmd_queue)
        tmp_cmd_queue = []
        tmp_val_queue = []
        tmp_arg_queue = []
        if q_length > 0:
            'first element of queue is the next command'
            next_cmd = cmd_queue[0]
            next_val = val_queue[0]
            next_args = arg_queue[0]
            a = 1
            while a < q_length:
                'add all elements but the first to the queue'
                set_entry(tmp_cmd_queue, a - 1, cmd_queue[a])
                set_entry(tmp_val_queue, a - 1, val_queue[a])
                set_entry(tmp_arg_queue, a - 1, arg_queue[a])
                a = a + 1
            end
            'update the queue'
            cmd_queue = tmp_cmd_queue
            val_queue = tmp_val_queue
            arg_queue = tmp_arg_queue

            if next_cmd == "movePos":
                print(f"movePos({next_val})")
            elif next_cmd == "movejJoints" or next_cmd == "movejPose":
                'trigger movej. arg defines if blend / time is used'
                if next_val == "nA":
                    print(f"movej({next_args}, acc, vel, 0, 0)")
                if next_val == "blend":
                    print(f"movej({next_args}, acc, vel, 0, blend)")
                if next_val == "time":
                    print(f"movej({next_args}, 1, 1, time, 0)")
                if next_val == "time,blend" or next_val == "blend,time":
                    print(f"movej({next_args}, 1, 1, time, blend)")
            elif next_cmd == "stopj":
                pass
                'doesnt work yet, because movej is blocking'
            elif next_cmd == "getPose":
                # actualPose = get_actual_tcp_pose()
                # socket_send_line(str_cat("returnValues:pose:", to_str(actualPose)), "rpi")
                cmd = "nA"
            elif next_cmd == "getJoints":
                # actualJoints = get_actual_joint_positions()
                # socket_send_line(str_cat("returnValues:joints:", to_str(actualJoints)), "rpi")
                cmd = "nA"


def thread3(cmd, val):
    global q_length, targetPose, targetJoints, vel, acc, blend, time, cmd_queue, val_queue, arg_queue
    if cmd == "x":
        targetPose[0] = to_num(val)
    elif cmd == "y":
        targetPose[1] = to_num(val)
    elif cmd == "z":
        targetPose[2] = to_num(val)
    elif cmd == "ax":
        targetPose[3] = to_num(val)
    elif cmd == "ay":
        targetPose[4] = to_num(val)
    elif cmd == "az":
        targetPose[5] = to_num(val)
    elif cmd == "j1":
        targetJoints[0] = to_num(val)
    elif cmd == "j2":
        targetJoints[1] = to_num(val)
    elif cmd == "j3":
        targetJoints[2] = to_num(val)
    elif cmd == "j4":
        targetJoints[3] = to_num(val)
    elif cmd == "j5":
        targetJoints[4] = to_num(val)
    elif cmd == "j6":
        targetJoints[5] = to_num(val)
    elif cmd == "vel":
        vel = to_num(val)
    elif cmd == "acc":
        acc = to_num(val)
    elif cmd == "time":
        time = to_num(val)
    elif cmd == "blend":
        blend = to_num(val)
    elif cmd == "gain":
        gain = to_num(val)
    elif cmd == "movejPose":
        set_entry(cmd_queue, q_length, cmd)
        set_entry(val_queue, q_length, val)
        set_entry(arg_queue, q_length, targetPose)
        q_length = get_list_length(cmd_queue)
    elif cmd == "movejJoints":
        set_entry(cmd_queue, q_length, cmd)
        set_entry(val_queue, q_length, val)
        set_entry(arg_queue, q_length, targetJoints)
        q_length = get_list_length(cmd_queue)


thread1()
