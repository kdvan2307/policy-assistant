"use client";

import { useEffect, useState } from "react";
import { getUsers, updateUserRole } from "@/services/api";

const ROLE_OPTIONS = ["admin", "security_manager", "employee", "guest"];

export default function UsersTab({ token }) {
  const [users, setUsers] = useState([]);
  const [errorByUser, setErrorByUser] = useState({});

  const loadUsers = async () => {
    try {
      const data = await getUsers(token);
      setUsers(data);
    } catch (error) {
      // im lặng — bảng trống là đủ thông báo cho người dùng thử lại
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    setErrorByUser((prev) => ({ ...prev, [userId]: null }));
    try {
      const updated = await updateUserRole(userId, newRole, token);
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
    } catch (error) {
      setErrorByUser((prev) => ({ ...prev, [userId]: error.message }));
      loadUsers(); // tải lại để đảm bảo UI khớp đúng dữ liệu thật trên server
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-slate-400 border-b border-slate-700">
          <tr>
            <th className="py-2 pr-4">Email</th>
            <th className="py-2 pr-4">Role</th>
            <th className="py-2 pr-4">Ngày tạo</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="border-b border-slate-800">
              <td className="py-2 pr-4">{user.email}</td>
              <td className="py-2 pr-4">
                <select
                  value={user.role}
                  onChange={(e) => handleRoleChange(user.id, e.target.value)}
                  className="px-2 py-1 rounded-lg bg-slate-800 border border-slate-700 text-white text-sm"
                >
                  {ROLE_OPTIONS.map((role) => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
                {errorByUser[user.id] && (
                  <p className="text-xs text-red-400 mt-1">{errorByUser[user.id]}</p>
                )}
              </td>
              <td className="py-2 pr-4 text-slate-400">
                {new Date(user.created_at).toLocaleDateString("vi-VN")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}