module("luci.controller.ip_hunter", package.seeall)

function index()
    entry(
        {"admin", "modem", "ip_hunter"},
        call("action_ip_hunter"),
        _("IP Hunter"),
        60
    ).dependent = false
end

function action_ip_hunter()
    local http = require "luci.http"
    local sys  = require "luci.sys"
    local fs   = require "nixio.fs"

    local target = http.formvalue("target_ip")
    local action = http.formvalue("action")

    if action == "run" and target and #target > 0 then
        -- simpan target
        local f = io.open("/tmp/ip_target.conf", "w")
        if f then
            f:write(target)
            f:close()
        end

        -- buat RUN flag
        fs.writefile("/tmp/ip_hunter.run", "1")

        -- jalankan background
        sys.call("python3 /usr/bin/modpes.py >/dev/null 2>&1 &")

    elseif action == "stop" then
        -- hapus RUN flag → script berhenti
        fs.remove("/tmp/ip_hunter.run")
    end

    -- baca IP list
    local ips = {}
    local f = io.open("/tmp/ip_hunter.list", "r")
    if f then
        for line in f:lines() do
            table.insert(ips, line)
        end
        f:close()
    end

    luci.template.render("ip_hunter", {
        ips = ips,
        target = target,
        running = fs.access("/tmp/ip_hunter.run")
    })
end
