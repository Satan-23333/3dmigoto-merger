# Author: SilentNightSound#7430
# Special Thanks:
#   Takoyaki#0697 (for demonstrating principle and creating the first proof of concept)
#   HazrateGolabi#1364 (for implementing the code to limit toggles to the on-screen character)

#   HummyR#8131, Modder4869#4818 (3.0+ Character Shader Fix)
# V3.0 of Mod Merger/Toggle Creator Script

# Merges multiple mods into one, which can be toggled in-game by pressing a key

# USAGE: Run this script in a folder which contains all the mods you want to merge
# So if you want to merge mods CharA, CharB, and CharC put all 3 folders in the same folder as this script and run it

# This script will automatically search through all subfolders to find mod ini files.
# It will not use .ini if that ini path/name contains "disabled"

# NOTE: This script will only function on mods generated using the 3dmigoto GIMI plugin

import os
import re
import argparse
import hashlib
import pyperclip as cb


def main():
    parser = argparse.ArgumentParser(
        description="Generates a merged mod from several mod folders"
    )
    parser.add_argument(
        "-r", "--root", type=str, default=".", help="Location to use to create mod"
    )
    parser.add_argument(
        "-s",
        "--store",
        action="store_true",
        help="Use to keep the original .ini files enabled after completion",
    )
    parser.add_argument(
        "-e", "--enable", action="store_true", help="Re-enable disabled .ini files"
    )
    parser.add_argument(
        "-n", "--name", type=str, default="merged.ini", help="Name of final .ini file"
    )
    parser.add_argument(
        "-k", "--key", type=str, default="", help="Key to press to switch mods"
    )
    parser.add_argument(
        "-c",
        "--compress",
        action="store_true",
        help="Makes the output mods as small as possible (warning: difficult to reverse, have backups)",
    )
    parser.add_argument(
        "-a",
        "--active",
        action="store_true",
        default=True,
        help="Only active character gets swapped when swapping)",
    )
    parser.add_argument(
        "-ref",
        "--reflection",
        action="store_true",
        help="Applies reflection fix for 3.0+ characters",
    )
    parser.add_argument(
        "-d", "--disable", action="store_true", help="Disable all .ini files"
    )

    args = parser.parse_args()

    print("\nGenshin Mod Merger/Toggle Creator Script\n")

    if args.active:
        print("Setting to swap only the active(on-screen) character")

    # enable_ini(args.root)

    if args.enable:
        print("Re-enabling all .ini files")
        enable_ini(args.root)
        print()

    if args.disable:
        print("Disabling all .ini files")
        disable_ini(args.root)
        return

    if not args.store:
        print(
            "\nWARNING: Once this script completes, it will disable all .ini files used to generate the merged mod (which is required in order for the final version to work without conflicts)"
        )
        print("You can prevent this behaviour by using the -s flag")
        print(
            "This script also has the ability to re-enable all mods in the current folder and all subfolders by using the -e flag - use this flag if you need to regenerate the merged ini again"
        )

    if args.compress:
        print(
            "\nWARNING2: The -c/--compress option makes the output smaller, but it will be difficult to retrieve the original mods from the merged one. MAKE SURE TO HAVE BACKUPS, and consider only using option after you are sure everything is good"
        )

    print("\nSearching for .ini files")
    ini_files = collect_ini(args.root, args.name)

    if not ini_files:
        print(
            "Found no .ini files - make sure the mod folders are in the same folder as this script."
        )
        print(
            "If using this script on a group of files that are already part of a toggle mod, use -e to enable .ini and regenerate the merge ini"
        )
        os.system("pause")
        return

    print(
        "\n你需要额外的控制功能吗？默认不需要\nDo you need an additional control method? No need by default.[y/N]"
    )
    extra = input()
    Is_swim = 0
    Is_nsfw = 0
    Is_namespace_merge = 0
    if extra == "y" or extra == "Y":
        print(
            "\n是否需要命名空间合并？默认不需要\nNeed to merge with namespace? No need by default. [y/N]"
        )
        Is_namespace_merge = input()
        if Is_namespace_merge == "y" or Is_namespace_merge == "Y":
            print("\n已激活\nActivated\n")
            Is_namespace_merge = 1
        else:
            print("\n已取消\nCancelled\n")
            Is_namespace_merge = 0

        print(
            "\n一键切换NSFW？默认不需要\nSwitch NSFW mods with one key? No need by default. [y/N]"
        )
        Is_nsfw = input()
        if Is_nsfw == "y" or Is_nsfw == "y":
            print("\n已激活\nActivated\n")
            Is_nsfw = 1
        else:
            print("\n已取消\nCancelled\n")
            Is_nsfw = 0

        print(
            "\n游泳切换？默认不需要\nAuto switch mods when swiming? No need by default. [y/N]"
        )
        Is_swim = input()
        if Is_swim == "y" or Is_swim == "y":
            print("\n游泳切换已激活\nSwim Activated\n")
            Is_swim = 1
        else:
            print("\n游泳切换已取消\nSwim Cancelled\n")
            Is_swim = 0

    for file in ini_files:
        if file != None:
            master_namespace, Poshash = get_position_name(str(file))
            if master_namespace:
                break

    if Is_namespace_merge:
        print(
            "\n输入命名空间,否则使用默认检测到的命名空间\nInput the namespace, otherwise use the default detected namespace"
        )
        input_namespace = input()
        if input_namespace:
            master_namespace = input_namespace
        ini_files = collect_ini(args.root, master_namespace + "merged")

    print("\nFound:")
    # if Is_namespace_merge:
    #     for i, namespace in enumerate(namespace_list):
    #         print(f"\t{i}:\t{namespace}")
    # else:
    for i, ini_file in enumerate(ini_files):
        print(f"\t{i}:\t{ini_file}")
    print(f"\nNamespace: {master_namespace}")
    print(
        "\nThis script will merge using the order listed above (0 is the default the mod will start with, and it will cycle 0,1,2,3,4,0,1...etc)"
    )
    print(
        "If this is fine, please press ENTER. If not, please enter the order you want the script to merge the mods (example: 3 0 1 2)"
    )
    print(
        "If you enter less than the total number, this script will only merge those listed.\n"
    )
    if Is_nsfw:
        print("输入sfw的mod\nInput the mods that is sfw.\n")
        ini_files_sfw, list_sfw = get_user_order(ini_files)
        Num_sfw = len(ini_files_sfw)

        for i, ini_file in enumerate(ini_files):
            if ini_file not in ini_files_sfw:
                print(f"\t{i}:  {ini_file}")
        print()
        print("输入nsfw的mod\nInput the mods that is nsfw.\n")
        ini_files_nsfw, list_nsfw = get_nsfw_order(ini_files, ini_files_sfw)
        ini_files = ini_files_sfw + ini_files_nsfw
        Num_ALL = len(ini_files)

        print(
            "输入切换nsfw的按键,默认是`\nPlease enter the key that will be used to swicth nsfw (can also set later in .ini). Key must be a single letter,default is `\n"
        )
        key_nsfw = input()
        while len(key_nsfw) > 1:
            print(
                "老铁，你输入的不对，必须是一个字符\nKey not recognized, must be a single letter\n"
            )
            key_nsfw = input()
        if not key_nsfw:
            key_nsfw = "`"
        else:
            key_nsfw = key_nsfw.lower()
    else:
        ini_files, list_sfw = get_user_order(ini_files)
        Num_sfw = Num_ALL = len(ini_files)

    if Is_namespace_merge:
        namespace_list = add_namespace_enable(ini_files, master_namespace)

    if Is_swim:
        print(
            "输入默认要显示的游泳mod，仅第1个\nInput the swimming MOD to be displayed by default, only the first.\n"
        )
        print()
        if Is_nsfw:
            for i, ini_file in enumerate(ini_files_sfw):
                print(f"\t{i}:  {ini_file}")
            print("SFW:\n")
            swim_set_sfw = input()
            if not swim_set_sfw:
                swim_set_sfw = Num_sfw - 1
            for i, ini_file in enumerate(ini_files_nsfw):
                print(f"\t{i+Num_sfw}:  {ini_file}")
            print("NSFW:\n")
            swim_set_nsfw = input()
            if not swim_set_nsfw:
                swim_set_nsfw = Num_ALL - 1
        else:
            for i, ini_file in enumerate(ini_files):
                print(f"\t{i}:  {ini_file}")
            print()
            swim_set_sfw = input()
        print(
            "输入开关游泳的按键,默认是 no_ctrl no_shift alt s\nPlease enter the key that will be used to swicth enable swim (can also set later in .ini). Key must be a single letter,default is no_ctrl no_shift alt s\n"
        )
        key_swim = input()
        while len(key_swim) > 1:
            print(
                "老铁，你输入的不对，必须是一个字符\nKey not recognized, must be a single letter\n"
            )
            key_swim = input()
        if not key_swim:
            key_swim = "no_ctrl no_shift alt s"
        else:
            key_swim = key_swim.lower()

    if args.key:
        key = args.key
    else:
        print(
            "输入手动切换mod的按键，默认是ctrl + 左右方向键\nPlease enter the key that will be used to cycle mods (can also enter this with -k flag, or set later in .ini). Key must be a single letter, default is ctrl + ← / →\n"
        )
        key = input()
        while len(key) > 1:
            print(
                "老铁，你输入的不对，必须是一个字符\nKey not recognized, must be a single letter\n"
            )
            key = input()
        if not key:
            key = "Key = ctrl no_shift no_alt VK_RIGHT"
        else:
            key = key.lower()

    constants = "\n; Constants ---------------------------\n\n"
    overrides = "; Overrides ---------------------------\n\n"
    shader = "; Shader ------------------------------\n\n"
    commands = "; CommandList -------------------------\n\n"
    resources = "; Resources ---------------------------\n\n"

    swapvar = "swapvar"

    constants += f"[Constants]\nglobal persist $swapvar = 0\n"
    if Is_nsfw or Is_swim:
        constants += f"global persist $t = 0\nglobal persist $temp_t = 0\n"
    if args.active:
        constants += f"global $active\n"
    if args.reflection:
        constants += f"global $reflection\n"
    if Is_nsfw:
        constants += f"""global persist $Num_sfw = {Num_sfw + 1 if Num_sfw == 1 else Num_sfw}
global persist $Num_ALL = {Num_ALL + 1 if Num_sfw == 1 else Num_ALL}
global $nsfw = 0
global persist $temp_nsfw = 0
global persist $last_sfw = 0
global persist $last_nsfw = {Num_sfw + 1 if Num_sfw == 1 else Num_sfw}

"""
    if Is_swim:
        if Is_nsfw:
            constants += f"""global $active_swim = 1
global $is_swim = 0
global persist $swim_temp = 0
global persist $swim_nsfw = 0
global persist $swim_set_sfw = {swim_set_sfw}
global persist $swim_set_nsfw = {swim_set_nsfw}
global persist $swim_pre_sfw = 0
global persist $swim_pre_nsfw = {Num_sfw + 1 if Num_sfw == 1 else Num_sfw}

"""
        else:
            constants += f"""
global $active_swim = 1
global $is_swim = 0
global persist $swim_temp = 0
global persist $swim_set_sfw = {swim_set_sfw}
global persist $swim_pre_sfw = 0

"""

    constants += f"\n[KeySwap]\n"
    if args.active:
        constants += f"condition = $active == 1\n"
    if len(key) == 1:
        constants += f"key = {key}\n"
    else:
        constants += f"Key = ctrl no_shift no_alt VK_RIGHT\nBack = ctrl no_shift no_alt VK_LEFT\n"
    if Is_nsfw or Is_swim:
        constants += f"type = cycle\n$t = {','.join([str(x) for x in range(Num_ALL + 1 if (Num_sfw == 1 or Num_ALL - Num_sfw == 1) and Is_nsfw == 1 else Num_ALL)])}\n\n"
    else:
        constants += f"type = cycle\n${swapvar} = {','.join([str(x) for x in range(Num_ALL)])}\n\n"
    if Is_nsfw:
        constants += f"""[KeyNSFW]
key = {key_nsfw}
type = cycle
$nsfw = 0,1

"""
    if Is_swim:
        constants += f"""[KeySwim]
key = {key_swim}
type = cycle
$active_swim = 0,1

"""

    if args.active or args.reflection or Is_nsfw:
        constants += f"[Present]\n"
    if args.active:
        constants += f"post $active = 0\n"
    if args.reflection:
        constants += f"post $reflection = 0\n"

    if args.active and (Is_nsfw or Is_swim):
        constants += "if $active == 1\n"
    if Is_swim:
        constants += """	if $active_swim == 1
		$is_swim = $\\global\\tracking\\swimming
	else
		$is_swim = 0
	endif

	if $is_swim == 1 && $swim_temp == 0
		$swim_temp = 1
		run = CommandListSwim
	elif $is_swim == 0 && $swim_temp == 1
		$swim_temp = 0
		run = CommandListSwim
	endif

"""
    if Is_nsfw:
        if Is_swim:
            constants += f"""
	if $nsfw != $temp_nsfw && $is_swim == 1
		if $nsfw == 1
			$temp_nsfw = 1
			$swim_set_sfw = $t
			$t = $swim_set_nsfw
		else
			$temp_nsfw = 0
			$swim_set_nsfw = $t
			$t = $swim_set_sfw
		endif
	endif

"""
        constants += f"""	if $nsfw == 0
		if $temp_nsfw == 1
			$t = $last_sfw
			$temp_nsfw = 0
		else
			if $t == $Num_sfw
				$t = 0
			elif $t >= $Num_sfw || $t < 0
				$t = $Num_sfw - 1
			endif

			if $last_sfw != $t {'&& ($active_swim == 0 || $active_swim == 1 && $is_swim == 0)' if Is_swim == 1 else ''}
				$last_sfw = $t
			endif
		endif
	else
		if $Num_ALL == $Num_sfw
			$nsfw = 0
		else
			if $temp_nsfw == 0
				$t = $last_nsfw
				$temp_nsfw = 1
			else
				if $t < $Num_sfw - 1 || $t >= $Num_ALL
					$t = $Num_sfw
				elif $t == $Num_sfw - 1
					$t = $Num_ALL - 1
				endif

				if $last_nsfw != $t {'&& ($active_swim == 0 || $active_swim == 1 && $is_swim == 0)' if Is_swim == 1 else ''}
					$last_nsfw = $t
				endif
			endif
		endif
	endif
"""
    if args.active and (Is_nsfw or Is_swim):
        constants += f"\tif $temp_t != $t\n\t\t$temp_t = $t\n\n"
        cnt = 0
        for i in range(Num_ALL + int(Is_nsfw == 1 and Num_sfw == 1)):
            if i == 0:
                constants += f"\t\tif $t == {i}\n\t\t    $swapvar = {i}\n\t\t    ;  {ini_files[i]}\n"
                cnt += 1
            else:
                if Is_nsfw == 1 and Num_sfw == 1:
                    constants += f"\t\telif $t == {i}\n\t\t    $swapvar = {i-1}\n\t\t    ;  {ini_files[i-1]}\n"
                    cnt += 1
                else:
                    constants += f"\t\telif $t == {i}\n\t\t    $swapvar = {i}\n\t\t    ;  {ini_files[i]}\n"
                    cnt += 1
        if Is_nsfw == 1 and Num_ALL - Num_sfw == 1:
            constants += f"\t\telif $t == {cnt}\n\t\t    $swapvar = {Num_ALL-1}\n\t\t    ;  {ini_files[-1]}\n"
        constants += "\t\tendif\n\n\tendif\n"
        constants += "endif\n"
    if Is_namespace_merge:
        constants += f"run = CommandList{master_namespace}Control\n"

    if Is_swim == 1:
        if Is_nsfw:
            constants += """[CommandListSwim]
if $swim_temp == 1
	if $nsfw == 0
		$swim_pre_sfw = $t
		$swim_pre_nsfw = $last_nsfw
		$t = $swim_set_sfw
	else
		$swim_pre_sfw = $last_sfw
		$swim_pre_nsfw = $t
		$t = $swim_set_nsfw
	endif
else
	if $nsfw == 0
		$swim_set_sfw = $t
		$t = $swim_pre_sfw
	else
		$swim_set_nsfw = $t
		$t = $swim_pre_nsfw
	endif
endif
"""
        else:
            constants += """[CommandListSwim]
if $swim_temp == 1
	$swim_pre_sfw = $t
	$t = $swim_set_sfw
else
	$swim_set_sfw = $t
	$t = $swim_pre_sfw
endif
"""

    result = "; Merged Mod: \n"
    # result += " ,\n".join([";  " + x for x in ini_files])
    if Is_nsfw:
        for i, ini_file in enumerate(ini_files_sfw):
            result += f"; {i}  \t{ini_file},\n"
        result += "; NSFW:\n"
        for i, ini_file in enumerate(ini_files_nsfw):
            result += f"; {i + Num_sfw}  \t{ini_file},\n"
    else:
        for i, ini_file in enumerate(ini_files):
            result += f"; {i}  \t{ini_file},\n"
    result += "; index: \n; "
    result += " ".join([str(x) for x in list_sfw])
    if Is_nsfw:
        result += "\n; "
        result += " ".join([str(x) for x in list_nsfw])
    result += f"\n\nnamespace={master_namespace}"
    result += constants

    if Is_namespace_merge:
        result += f"\n[CommandList{master_namespace}Control]\n"
        for i in range(len(namespace_list)):
            result += f"\n    ;{i}:\t{ini_files[i]}:↓\n"
            result += f"if $swapvar == {i}\n\t$\\{namespace_list[i]}\\enable_this = 1\nelse\n\t$\\{namespace_list[i]}\\enable_this = 0\nendif\n"
        result += f"\n[TextureOverride{master_namespace}Position]\n"
        result += f"{Poshash}"
        result += f"$active = 1\n\n"
        result += "; .ini generated by GIMI (Genshin-Impact-Model-Importer) mod merger script, Original by SilentNightSoundand, Edit by 夏科, Discord:satan_2333\n; Github: https://github.com/Satan-23333/3dmigoto-merger\n"
        result += "; If you have any issues or find any bugs, please open a ticket at https://github.com/Satan-23333/3dmigoto-merger/issues or contact satan_2333 on discord"

        with open(master_namespace + "merged.ini", "w", encoding="utf-8") as f:
            f.write(result)

        if not args.store:
            print("Cleanup and disabling ini")
            for file in ini_files:
                os.rename(
                    file,
                    os.path.join(os.path.dirname(file), "DISABLED")
                    + os.path.basename(file),
                )
        print("All operations completed")
        os.system("pause")
        return

    print("Parsing ini sections")
    all_mod_data = []
    ini_group = 0
    for ini_file in ini_files:
        with open(ini_file, "r", encoding="utf-8") as f:
            ini_text = ["[" + x.strip() for x in f.read().split("[")]
            for section in ini_text[1:]:
                mod_data = parse_section(section)
                mod_data["location"] = os.path.dirname(ini_file)
                mod_data["ini_group"] = ini_group
                all_mod_data.append(mod_data)
        ini_group += 1

    # if [x for x in all_mod_data if "name" in x and x["name"].lower() == "creditinfo"]:
    #     constants += "run = CommandListCreditInfo\n\n"
    # else:
    #     constants += "\n"

    if [x for x in all_mod_data if "name" in x and x["name"].lower() == "transparency"]:
        shader += """[CustomShaderTransparency]
blend = ADD BLEND_FACTOR INV_BLEND_FACTOR
blend_factor[0] = 0.5
blend_factor[1] = 0.5
blend_factor[2] = 0.5
blend_factor[3] = 1
handling = skip
drawindexed = auto

"""

    print("Calculating overrides and resources")
    command_data = {}
    seen_hashes = {}
    reflection = {}
    n = 1
    for i in range(len(all_mod_data)):
        # Overrides. Since we need these to generate the command lists later, need to store the data
        if "hash" in all_mod_data[i]:
            index = -1
            if "match_first_index" in all_mod_data[i]:
                index = all_mod_data[i]["match_first_index"]
            # First time we have seen this hash, need to add it to overrides
            if (all_mod_data[i]["hash"], index) not in command_data:
                command_data[(all_mod_data[i]["hash"], index)] = [all_mod_data[i]]
                overrides += f"[{all_mod_data[i]['header']}{all_mod_data[i]['name']}]\nhash = {all_mod_data[i]['hash']}\n"
                if index != -1:
                    overrides += f"match_first_index = {index}\n"
                # These are custom commands GIMI implements, they do not need a corresponding command list
                if "VertexLimitRaise" not in all_mod_data[i]["name"]:
                    overrides += f"run = CommandList{all_mod_data[i]['name']}\n"
                if index != -1 and args.reflection:
                    overrides += f"ResourceRef{all_mod_data[i]['name']}Diffuse = reference ps-t1\nResourceRef{all_mod_data[i]['name']}LightMap = reference ps-t2\n$reflection = {n}\n"
                    reflection[all_mod_data[i]["name"]] = (
                        f"ResourceRef{all_mod_data[i]['name']}Diffuse,ResourceRef{all_mod_data[i]['name']}LightMap,{n}"
                    )
                    n += 1
                if args.active:
                    if "Position" in all_mod_data[i]["name"]:
                        overrides += f"$active = 1\n"

                overrides += "\n"
            # Otherwise, we have seen the hash before and we just need to append it to the commandlist
            else:
                command_data[(all_mod_data[i]["hash"], index)].append(all_mod_data[i])
        elif "header" in all_mod_data[i] and "CommandList" in all_mod_data[i]["header"]:
            command_data.setdefault((all_mod_data[i]["name"], 0), []).append(
                all_mod_data[i]
            )
        # Resources
        elif "filename" in all_mod_data[i] or "type" in all_mod_data[i]:
            resources += f"[{all_mod_data[i]['header']}{all_mod_data[i]['name']}.{all_mod_data[i]['ini_group']}]\n"
            for command in all_mod_data[i]:
                if command in ["header", "name", "location", "ini_group"]:
                    continue
                if command == "filename":
                    with open(
                        f"{all_mod_data[i]['location']}\\{all_mod_data[i][command]}",
                        "rb",
                    ) as f:
                        sha1 = hashlib.sha1(f.read()).hexdigest()
                    if sha1 in seen_hashes and args.compress:
                        resources += f"{command} = {seen_hashes[sha1]}\n"
                        os.remove(
                            f"{all_mod_data[i]['location']}\\{all_mod_data[i][command]}"
                        )
                    else:
                        seen_hashes[sha1] = (
                            f"{all_mod_data[i]['location']}\\{all_mod_data[i][command]}"
                        )
                        resources += f"{command} = {all_mod_data[i]['location']}\\{all_mod_data[i][command]}\n"
                else:
                    resources += f"{command} = {all_mod_data[i][command]}\n"
            resources += "\n"

    if args.reflection:
        print("Character Shader Fix")
        refresources = ""
        CommandPart = ["ReflectionTexture", "Outline"]
        shadercode = r"""
[ShaderRegexCharReflection]
shader_model = ps_5_0
run = CommandListReflectionTexture
[ShaderRegexCharReflection.pattern]
discard_n\w+ r\d\.\w+\\n
lt r\d\.\w+, l\(0\.010000\), r\d\.\w+\\n
and r\d\.\w+, r\d\.\w+, r\d\.\w+\\n

[ShaderRegexCharOutline]
shader_model = ps_5_0
run = CommandListOutline
[ShaderRegexCharOutline.pattern]
mov o0\.w, l\(0\)\\n
mov o1\.xyz, r0\.xyzx\\n
		"""
        shader += f"{shadercode}\n"
        for i in range(len(CommandPart)):
            ref = f"[CommandList{CommandPart[i]}]\n"
            ref += f"if $reflection != 0\n\tif "
            for x in reflection:
                r = reflection[x].split(",")
                ref += f"$reflection == {r[2]}\n"
                ps = [["ps-t0", "ps-t1"], ["ps-t1", "ps-t2"]]
                ref += f"\t\t{ps[i][0]} = copy {r[0]}\n\t\t{ps[i][1]} = copy {r[1]}\n"
                ref += f"\telse if "
                if i == 0:
                    refresources += f"[{r[0]}]\n[{r[1]}]\n"
            ref = ref.rsplit("else if", 1)[0] + "endif\n"
            ref += f"drawindexed=auto\n"
            ref += f"$reflection = 0\n"
            ref += f"endif\n\n"
            commands += ref

    print("Constructing command lists")
    tabs = 1

    for hash, index in command_data:
        if "VertexLimitRaise" in command_data[(hash, index)][0]["name"]:
            continue
        commands += f"[CommandList{command_data[(hash, index)][0]['name']}]\nif "
        for model in command_data[(hash, index)]:
            commands += f"${swapvar} == {model['ini_group']}\n"
            for command in model:
                if command in [
                    "header",
                    "name",
                    "hash",
                    "match_first_index",
                    "location",
                    "ini_group",
                ]:
                    continue

                if command == "endif":
                    tabs -= 1
                    for i in range(tabs):
                        commands += "\t"
                    commands += f"{command}"
                elif "else if" in command:
                    tabs -= 1
                    for i in range(tabs):
                        commands += "\t"
                    commands += f"{command} = {model[command]}"
                    tabs += 1
                else:
                    for i in range(tabs):
                        commands += "\t"
                    if command[:2] == "if" or command[:7] == "else if":
                        commands += f"{command} == {model[command]}"
                    else:
                        commands += f"{command} = {model[command]}"
                    if command[:2] == "if":
                        tabs += 1
                    elif (
                        command[:2] in ["vb", "ib", "ps", "vs", "th"]
                        or "Resource" in model[command]
                    ) and model[command].lower() != "null":
                        commands += f".{model['ini_group']}"
                commands += "\n"
            commands += "else if "
        commands = commands.rsplit("else if", 1)[0] + "endif\n\n"

    print("Printing results")
    if args.reflection:
        result += f"{refresources}\n"
    result += shader
    result += overrides
    result += commands
    result += resources
    if args.reflection:
        result += "\n\n; For fixing green reflections and broken outlines colors on 3.0+ characters\n"
    else:
        result += "\n\n"
    result += (
        "; .ini generated by GIMI (Genshin-Impact-Model-Importer) mod merger script\n"
    )

    result += "; If you have any issues or find any bugs, please open a ticket at https://github.com/SilentNightSound/GI-Model-Importer/issues or contact SilentNightSound#7430 on discord"

    with open(args.name, "w", encoding="utf-8") as f:
        f.write(result)

    if not args.store:
        print("Cleanup and disabling ini")
        for file in ini_files:
            os.rename(
                file,
                os.path.join(os.path.dirname(file), "DISABLED")
                + os.path.basename(file),
            )

    print("All operations completed")
    os.system("pause")


# Collects all .ini files from current folder and subfolders
def collect_ini(path, ignore):
    ini_files = []
    for root, dir, files in os.walk(path):
        if "disabled" in root.lower():
            continue
        for file in files:
            if "disabled" in file.lower() or ignore.lower() in file.lower():
                continue
            if os.path.splitext(file)[1] == ".ini":
                if "with_namespace_enable" in file.lower():
                    os.remove(os.path.join(root, file))
                    continue
                ini_files.append(os.path.join(root, file))
    return ini_files


# Re-enables disabled ini files
def enable_ini(path):
    for root, dir, files in os.walk(path):
        if "disabled" in root.lower():
            continue
        for file in files:
            if os.path.splitext(file)[1] == ".ini" and ("disabled" in file.lower()):
                print(f"\tRe-enabling {os.path.join(root, file)}")
                new_path = re.compile("disabled", re.IGNORECASE).sub(
                    "", os.path.join(root, file)
                )
                os.rename(os.path.join(root, file), new_path)


def disable_ini(path):
    for root, dir, files in os.walk(path):
        if "disabled" in root.lower():
            continue
        for file in files:
            if os.path.splitext(file)[1] == ".ini" and not file.lower().startswith(
                ("disabled", "merged") and "with_namespace_enable" not in file.lower()
            ):
                print(f"\tDisabling {os.path.join(root, file)}")
                file_path = os.path.join(root, file)
                new_file_name = "DISABLED" + file
                new_file_path = os.path.join(root, new_file_name)
                os.rename(file_path, new_file_path)
                # os.rename(file, os.path.join(os.path.dirname(file), "DISABLED") + os.path.basename(file))
    print("Disable completed")


# Gets the user's preferred order to merge mod files
def get_user_order(ini_files):
    choice = input()

    # User entered data before pressing enter
    while choice:
        choice = choice.strip().split(" ")

        if len(choice) > len(ini_files):
            print("\nERROR: please only enter up to the number of the original mods\n")
            choice = input()
        else:
            try:
                result = []
                if choice[0] == "y" or choice[0] == "Y":
                    get_merged_list(ini_files)
                choice = [int(x) for x in choice]
                if len(set(choice)) != len(choice):
                    print("\nERROR: please enter each mod number at most once\n")
                    choice = input()
                elif max(choice) >= len(ini_files):
                    print(
                        "\nERROR: selected index is greater than the largest available\n"
                    )
                    choice = input()
                elif min(choice) < 0:
                    print("\nERROR: selected index is less than 0\n")
                    choice = input()
                    print()
                else:
                    for x in choice:
                        result.append(ini_files[x])
                    return result, choice
            except ValueError:
                if choice[0] == "y" or choice[0] == "Y":
                    print("\n看来你发现了隐藏功能，检查你的剪贴板并修改他们")
                    for i, ini_file in enumerate(ini_files):
                        print(f"\t{i}:  {ini_file}")
                print(
                    "\nERROR: please only enter the index of the mods you want to merge separated by spaces (example: 3 0 1 2)\n"
                )
                choice = input()

    # User didn't enter anything and just pressed enter
    choice = list(range(len(ini_files)))
    return ini_files, choice


def get_nsfw_order(ini_files, ini_files_sfw):
    choice = input()

    # User entered data before pressing enter
    while choice:
        choice = choice.strip().split(" ")

        if len(choice) > len(ini_files):
            print("\nERROR: please only enter up to the number of the original mods\n")
            choice = input()
        else:
            try:
                result = []
                choice = [int(x) for x in choice]
                if len(set(choice)) != len(choice):
                    print("\nERROR: please enter each mod number at most once\n")
                    choice = input()
                elif max(choice) >= len(ini_files):
                    print(
                        "\nERROR: selected index is greater than the largest available\n"
                    )
                    choice = input()
                elif min(choice) < 0:
                    print("\nERROR: selected index is less than 0\n")
                    choice = input()
                    print()
                else:
                    for x in choice:
                        result.append(ini_files[x])
                    return result, choice
            except ValueError:
                print(
                    "\nERROR: please only enter the index of the mods you want to merge separated by spaces (example: 3 0 1 2)\n"
                )
                choice = input()

    # User didn't enter anything and just pressed enter
    choice = list(range(len(ini_files)))
    ini_files_copy = ini_files.copy()
    for i, ini_file in enumerate(ini_files):
        if ini_file in ini_files_sfw:
            ini_files_copy.remove(ini_file)
            choice.remove(i)

    return ini_files_copy, choice


# Parses a section from the .ini file
def parse_section(section):
    mod_data = {}
    recognized_header = (
        "[TextureOverride",
        "[ShaderOverride",
        "[Resource",
        "[Constants",
        "[Present",
        "[CommandList",
        "[CustomShader",
    )
    for line in section.splitlines():
        if not line.strip() or line[0] == ";":  # comments and empty lines
            continue

        # Headers
        for header in recognized_header:
            if header in line:
                # I give up on trying to merge the reflection fix, it's way too much work. Just re-apply after merging
                if (
                    "CommandListReflectionTexture" in line
                    or "CommandListOutline" in line
                ):
                    return {}
                mod_data["header"] = header[1:]
                mod_data["name"] = line.split(header)[1][:-1]
                break
        # Conditionals
        if "==" in line:
            key, data = line.split("==", 1)
            mod_data[key.strip()] = data.strip()
        elif "endif" in line:
            key, data = "endif", ""
            mod_data[key.strip()] = data.strip()
        # Properties
        elif "=" in line:
            key, data = line.split("=")
            # See note on reflection fix above
            if "CharacterIB" in key or "ResourceRef" in key:
                continue

            mod_data[key.strip()] = data.strip()

    return mod_data


def get_merged_list(ini_files):
    merged_path = "./merged.ini"
    merged_ini_files = ""
    with open(merged_path, "r", encoding="utf-8") as f:
        content = ""
        while (
            content != "; Constants ---------------------------\n"
            and content != "; index: \n"
        ):
            content = f.readline()
            merged_ini_files += content

    merged_ini_files = merged_ini_files.split("Merged Mod:")[1]
    if "nsfw:" in merged_ini_files.lower():
        nsfw_ini_files = (
            ".\\"
            + merged_ini_files.split(":")[1]
            .split(".ini")[0]
            .split(".\\")[-1]
            .rstrip(",")
            + ".ini"
        )
        # nsfw_ini_files = [
        #     ".\\" + ini.split(".\\")[-1].rstrip(",") + ".ini"
        #     for ini in merged_ini_files.split(":")[1].split(".ini")[:-1]
        # ]
    merged_ini_files = merged_ini_files.split(".ini")[:-1]
    merged_ini_files = [
        ".\\" + ini.split(".\\")[-1].rstrip(",") + ".ini" for ini in merged_ini_files
    ]

    merged_ini_list = []
    for ini in merged_ini_files:
        if ini in ini_files:
            merged_ini_list.append(ini_files.index(ini))
    try:
        merged_ini_list.insert(merged_ini_files.index(nsfw_ini_files), "\n")
    except:
        print("Warning")
    x = ""
    for i in merged_ini_list:
        x += str(i) + " "
    cb.copy(x)
    return merged_ini_list


def add_namespace_enable(ini_files, master_namespace):
    namespace_list = []
    for i, file in enumerate(ini_files):
        if "with_namespace_enable" in file:
            # os.remove(file)
            continue
        # print("file:", file)
        with open(file, "r", encoding="utf-8") as f:
            ini_lines = f.readlines()
        namespace = f"{master_namespace}{file.lstrip('.').rstrip('.ini')}"
        namespace_list.append(namespace)
        content, namespace = modify_namespace(ini_lines, namespace, i)
        # print("namespace:", namespace, "\n")
        # if "namespace" not in content:
        #     with open(file, "w", encoding="utf-8") as f:
        #         f.write("namespace=mod\n" + content)

        new_file_path = (
            os.path.join(os.path.dirname(file))
            + "\\"
            + os.path.splitext(os.path.basename(file))[0]
            + "_with_namespace_enable.ini"
        )
        with open(new_file_path, "w", encoding="utf-8") as file:
            file.write(content)

    print("Namespace added to all ini files")
    return namespace_list


def modify_namespace(ini_lines, namespace, num):
    content = ""
    temp = ""
    original = ""
    addif = 0
    add_condition = 0
    add_namespace = 1
    add_constants = 1
    internal_namespace = namespace
    for line in ini_lines:
        strip_line = line.strip()
        if strip_line.startswith("namespace"):
            add_namespace = 0
            internal_namespace = strip_line.split("=")[1].strip()
        if strip_line.startswith("[") and strip_line.endswith("]"):
            content += (
                (
                    "endif\n"
                    if addif
                    else (
                        "condition = $enable_this == 1\n" if add_condition == 1 else ""
                    )
                )
                + original
                + line
            )
            if "constants" in strip_line.lower():
                content += "global persist $enable_this = 0\n"
                add_constants = 0
            if strip_line.lower().startswith("[key"):
                add_condition = 1
                # content += "condition = $enable_this == 1\n"
            else:
                add_condition = 0
            if (
                "textureoverride" in strip_line.lower()
                or "present" in strip_line.lower()
            ):
                # if "present" in strip_line.lower():
                #     content += f"if ${namespace} == 1\n"
                #     content += "    $enable_this = 1\n"
                #     content += "else\n"
                #     content += "    $enable_this = 0\n"
                #     content += "endif\n"
                addif = 1
                content += "if $enable_this == 1\n"
            else:
                addif = 0
            original = ""
            temp = ""
        elif addif:
            if line.strip().lower().startswith(
                "hash ="
            ) or line.strip().lower().startswith("hash="):
                content += temp + "    " + line + "    " + f"match_priority = {num}\n"
                temp = ""
                original = ""

            elif line.lower().startswith("match_priority"):
                continue
            elif strip_line == "" or strip_line.startswith(";"):
                temp += "    " + line
                original += line
            else:
                content += temp + "    " + line
                temp = ""
                original = ""
        elif add_condition:
            if strip_line.startswith("condition"):
                original_condition = (
                    strip_line.split("condition")[1].strip().strip("=").strip()
                )
                new_condition = f"({original_condition}) && $enable_this == 1"
                original += f"condition = {new_condition}\n"
                add_condition = 0
            else:
                original += line
        else:
            original += line
    content += ("endif\n" if addif else "") + original
    addition = ""
    if add_namespace:
        addition += f"namespace = {namespace}\n"
    if add_constants:
        addition += "\n[Constants]\n"
        addition += "global persist $enable_this = 0\n\n"

    content = addition + content
    return content, internal_namespace


def get_position_name(path):
    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        found = False
        hash = ""
        for line in lines:
            # Ends the if when a line with [] or ; is found
            if line.startswith("[TextureOverride") and line.endswith("Position]\n"):
                found = line.split("TextureOverride")[1].split("Position")[0]
            if line.strip().lower().startswith(
                "hash ="
            ) or line.strip().lower().startswith("hash="):
                hash = line
                if found:
                    return found, hash
    #         return line
    # return ";None found\n"
    return found, hash


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        os.system("pause")
